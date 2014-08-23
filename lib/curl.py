import lib.sys

CMD_CURL = ["curl"]
FLAG_VERBOSE = ["-v"]
METHOD_GET = "GET"
METHOD_POST = "POST"
METHOD_UPDATE = "UPDATE"
METHOD_DELETE = "DELETE"

def body(data):
	if data is not None : return ["-d", data]
	else : return []

def resource(contenttype, url):
	return ["-H", "Content-Type: %s" % contenttype, url]

def auth(username = None, password = None):
	if username is None : return []
	elif password is None : return ["-u", username]
	else : return ["-u", "%s:%s" % (username, password)]

def request(method):
	return ["-X", method]

def call(method, url, contenttype, data = None, username = None, password = None, **kwargs):

	cmd = []
	cmd.extend(CMD_CURL)
	cmd.extend(request(method))
	cmd.extend(FLAG_VERBOSE)
	cmd.extend(auth(username, password))
	cmd.extend(resource(contenttype, url))
	cmd.extend(body(data))

	return lib.sys.call(cmd, **kwargs)


def json(method, url, data = None, username = None, password = None, **kwargs):
	return call(method, url, "application/json", data, username, password, **kwargs)

def getjson(url, data = None, username = None, password = None, **kwargs):
	return json(METHOD_GET, url, data, username, password, **kwargs)

def postjson(url, data = None, username = None, password = None, **kwargs):
	return json(METHOD_POST, url, data, username, password, **kwargs)