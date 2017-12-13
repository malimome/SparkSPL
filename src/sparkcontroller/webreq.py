import requests


#TODO Create connection pool
def get_req(url, data=None, header=None):
    print("%s %s"%("GET", url))
    resp = None
    try:
        resp = requests.get(url, params=data, headers=header)
        if resp.status_code not in [200, 201]:
            raise ReferenceError(resp.content)
    except ConnectionError as ex:
        raise ex
    except AttributeError as ex:
        raise ReferenceError("Corrupted response!")
    return resp


def post_req(url, data=None, json=None, header=None):
    print("%s %s" % ("POST", url))
    resp = requests.post(url, data=data, json=json, headers=header)
    if resp.status_code not in [200, 201]:
        raise Exception(str(resp))
    return resp


def delete_req(url, data=None, header=None):
    print("%s %s" % ("DEL", url))
    resp = requests.delete(url, headers=header)
    if resp.status_code not in [200, 201]:
        raise Exception(str(resp))
    return resp

