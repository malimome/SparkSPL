import requests
reqsession = requests.Session()
reqsession.mount('http://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=50))


#TODO Create connection pool
def get_req(url, param=None, header=None):
    print("%s %s"%("GET", url))
    resp = None
    try:
        resp = reqsession.get(url, params=param, headers=header)
        if resp.status_code not in [200, 201]:
            raise Exception(resp.content)
    except ConnectionError as ex:
        raise ex
    return resp


def post_req(url, data=None, json=None, header=None):
    print("%s %s" % ("POST", url))
    resp = None
    try:
        resp = reqsession.post(url, data=data, json=json, headers=header)
        if resp.status_code not in [200, 201]:
            raise Exception(str(resp))
    except ConnectionError as ex:
        raise ex
    return resp


def put_req(url, data=None, json=None, header=None):
    print("%s %s" % ("PUT", url))
    resp = None
    try:
        resp = reqsession.put(url, data=data, json=json, headers=header)
        if resp.status_code not in [200, 201]:
            raise Exception(str(resp))
    except ConnectionError as ex:
        raise ex
    return resp


def delete_req(url, data=None, header=None):
    print("%s %s" % ("DEL", url))
    resp = None
    try:
        resp = reqsession.delete(url, headers=header)
        if resp.status_code not in [200, 201]:
            raise Exception(str(resp))
    except ConnectionError as ex:
        raise ex
    return resp
