import ftplib, getpass, project.file, json, os, base64, tempfile

def __ftp_is_file(ftp, path):
	if len(path) == 0 or path[0] != '/' : path = ftp.pwd() + '/' + path
	l = ftp.nlst(path)
	return len(l) == 1 and l[0] == path

def __ftp_is_dir(ftp, path):
	if len(path) == 0 or path[0] != '/' : path = ftp.pwd() + '/' + path
	l = ftp.nlst(path)
	return len(l) > 0 and l[0] != path


def __local_fetch(root, config, checksum_table, hierarchy_tree, current = '', tree = None):
	if tree == None : tree = config['tree']
	dir_list = os.listdir(root + '/' + current)
	print(dir_list)
	for item, what in tree.items():
		minipath = current + item
		path = root + '/' + minipath
		if os.path.isfile(path):
			base, ext = os.path.splitext(minipath)
			if ext == config['online_ext'] : dest = base
			elif item + config['online_ext'] in dir_list : continue
			else : dest = minipath
			with open(path, 'rb') as f:
				checksum = project.file.checksum(f).digest()
			checksum_ascii = base64.b64encode(checksum).decode('ascii')
			checksum_table.setdefault(checksum_ascii, {'s' : [], 'd' : []})
			checksum_table[checksum_ascii]['s'].append(minipath)
			checksum_table[checksum_ascii]['d'].append(dest)
			hierarchy_tree[item] = [checksum_ascii, dest]

		elif os.path.isdir(path):
			if what == None : what = { sub : None for sub in os.listdir(path)}
			hierarchy_tree[item] = {}
			__local_fetch(root, config, checksum_table, hierarchy_tree[item], current + item + '/', what)


def __server_fetch(ftp, config, server, current = ''):
	checksum_file = '/%s/%s' % (config['root'], config['checksum'])
	if __ftp_is_file(ftp, checksum_file):
		chuncks = []
		ftp.retrlines('RETR %s' % checksum_file, chuncks.append)
		checksum = ''.join(chuncks)
		data = json.loads(checksum)
		server['checksum_table'] = data['checksum_table']
		server['hierarchy_tree'] = data['hierarchy_tree']


def __update_deleted_moved_copied(ftp, config, local, server):
	for checksum, minipaths in server['checksum_table'].items():

		# deleted files
		if checksum not in local['checksum_table']:
			for i in range(len(minipaths)):
				print('ftp.delete(\'/%s/%s\')' % (config['root'], minipaths[i]))
				# ftp.delete('/%s/%s' % (config['root'], minipaths[i]))

		else:

			base = None
			not_handled = local['checksum_table']['d'].copy()

			for i in range(len(minipaths)):
				minipath = minipaths[i]

				# moved files
				if minipath not in local['checksum_table']['d']:
					if len(not_handled) > 0:
						for j in range(len(not_handled)):
							if not_handled[j] not in minipaths:
								replace = not_handled[j]
								del not_handled[j]
								break

						print('ftp.rename(\'/%s/%s\', \'/%s/%s\')' % (config['root'], minipath, config['root'], replace))
						# ftp.rename('/%s/%s' % (config['root'], minipath), '/%s/%s' % (config['root'], replace))
					else:
						print('ftp.delete(\'/%s/%s\')' % (config['root'], minipath))
						# ftp.delete('/%s/%s' % (config['root'], minipath)

				# not moved
				else:
					base = minipath
					not_handled.remove(minipath)

			# copied files
			for i in range(len(not_handled)):
				print('ftp.copy(\'/%s/%s\', \'/%s/%s\')' % (config['root'], base, config['root'], not_handled[i]))
				# ftp.copy('/%s/%s' % (config['root'], base), '/%s/%s' % (config['root'], not_handled[i]))


def __update_added(ftp, config, local, server):
	for checksum, paths in local['checksum_table'].items():
		# added files
		if checksum not in server['checksum_table']:
			for i in range(len(paths['s'])):
				with open('%s/%s' % (local['root'], paths['s'][i]), 'rb') as f:
					print('ftp.storbinary(\'STOR /%s/%s\', %s)' % (config['root'], paths['d'][i], f))
					# ftp.storbinary('STOR /%s/%s' % (config['root'], paths[i]['d']), f)

def __update_modified(ftp, config, local_h, server_h, current = ''):

	for item, data in local_h.items():
		# modified files
		if type(data) == list:
			checksum, dest = data
			if dest in server_h and checksum != server_h[dest]:
				with open('%s/%s%s' % (local['root'], current, item), 'rb') as f:
					print('ftp.storbinary(\'STOR /%s/%s\', %s)' % (config['root'], current, dest, f))
					# ftp.storbinary('STOR /%s/%s' % (config['root'], minipath), f)


		elif item in server_h:
			__update_modified(ftp, config, data, server_h[item], current + item + '/')

def __update_checksum(ftp, config, local):
	data = {
		'checksum_table' : local['checksum_table'],
		'hierarchy_tree' : local['hierarchy_tree']
	}
	with open('%s/%s' % (local['root'], config['checksum']), 'w') as f:
		json.dump(data, f, indent = '\t')
		f.seek(0)
		print('ftp.storbinary(\'STOR /%s/%s\', %s)' % (config['root'], config['checksum'], f))
		# ftp.storbinary('STOR /%s/%s' % (config['root'], config['checksum']), f)


def __update(ftp, config, local, server):
	__update_deleted_moved_copied(ftp, config, local, server)
	__update_added(ftp, config, local, server)
	# __update_modified(ftp, config, local['hierarchy_tree'], server['hierarchy_tree'])
	__update_checksum(ftp, config, local)


def up(directory, config_file):

	local = {
		'root' : os.path.abspath(directory),
		'checksum_table' : {},
		'hierarchy_tree' : {}
	}

	# fetch the file tree to upload
	with open(config_file, 'r') as f:
		config = json.load(f)

	# build the local tree and table
	__local_fetch(local['root'], config, local['checksum_table'], local['hierarchy_tree'])

	print(json.dumps(local['checksum_table'], indent = '\t'))
	print(json.dumps(local['hierarchy_tree'], indent = '\t'))

	try:

		ftp = ftplib.FTP()
		ftp.connect(config['host'])
		print(ftp.getwelcome())
		username = config['username'] if 'username' in config else input('Username for \'ftp://%s\' : ' % (config['host']))
		password = getpass.getpass('Password for \'ftp://%s@%s\' : ' % (username, config['host']))
		ftp.login(username, password)
		ftp.cwd(config['root'])


		server = {
			'root' : os.path.abspath(directory),
			'checksum_table' : {},
			'hierarchy_tree' : {}
		}

		# build the server tree and table
		__server_fetch(ftp, config, server['checksum_table'], server['hierarchy_tree'])

		print(json.dumps(server['checksum_table'], indent = '\t'))
		print(json.dumps(server['hierarchy_tree'], indent = '\t'))


		__update(ftp, config, local, server)

	# except ftplib.all_errors as e:
	# 	print('Socket error : %s' % (e))

	finally:
		ftp.quit()

# FTP.rename(fromname, toname)
# FTP.delete(filename)
# FTP.mkd(pathname)
# FTP.rmd(dirname)