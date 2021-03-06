
import lib.sys
import json
import functools

CMD_CURL = ["curl"]
FLAG_VERBOSE = ["-v"]
PUT = "PUT"
GET = "GET"
POST = "POST"
PATCH = "PATCH"
UPDATE = "UPDATE"
DELETE = "DELETE"


def body(data):
    if data is not None:
        return ["-d", data]
    else:
        return []


def resource(contenttype, location, url, accept=None):

    params = header("Content-Type", contenttype)
    params += header("Accept", accept)

    if location:
        params.append("-L")

    params.append(url)

    return params


def auth(username=None, password=None):
    if username is None:
        return []
    elif password is None:
        return ["-u", username]
    else:
        return ["-u", "%s:%s" % (username, password)]

def header ( key , value ):
    if value is None:
        return []
    else:
        return ["-H", "{}: {}".format(key, value)]

def request(method):
    return ["-X", method]


def call(method, url, contenttype, data=None, username=None, password=None,
        location=False, accept=None, authorization=None, **kwargs):

    cmd = []
    cmd.extend(CMD_CURL)
    cmd.extend(request(method))
    cmd.extend(FLAG_VERBOSE)
    cmd.extend(auth(username, password))
    cmd.extend(header('Authorization', authorization))
    cmd.extend(resource(contenttype, location, url, accept=accept))
    cmd.extend(body(data))

    return lib.sys.call(cmd, **kwargs)


def sendjson(method, url, data=None, username=None, password=None, **kwargs):
    if data is not None:
        data = json.dumps(data)
    return call(method, url, "application/json", data, username, password, **kwargs)

putjson = functools.partial(sendjson, PUT)
getjson = functools.partial(sendjson, GET)
postjson = functools.partial(sendjson, POST)
updatejson = functools.partial(sendjson, UPDATE)
patchjson = functools.partial(sendjson, PATCH)
deletejson = functools.partial(sendjson, DELETE)
