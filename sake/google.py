from __future__ import absolute_import, division, print_function, unicode_literals

import sake

def search(s):
	sake.navigator.open("https://google.com#q=%s" % s);