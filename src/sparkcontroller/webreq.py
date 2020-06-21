import logging

import requests
from requests.adapters import HTTPAdapter

import settings

log = logging.getLogger(__name__)

reqsession = requests.Session()
reqsession.mount("http://", HTTPAdapter(pool_connections=10, pool_maxsize=50))
reqsession.mount("https://", HTTPAdapter(pool_connections=10, pool_maxsize=50))


class UpstreamError(Exception):
    """An upstream service (Livy, Elasticsearch) failed or was unreachable."""


def _request(method, url, **kwargs):
    log.debug("%s %s", method, url)
    kwargs.setdefault("timeout", settings.HTTP_TIMEOUT)
    try:
        resp = reqsession.request(method, url, **kwargs)
    except requests.RequestException as ex:
        raise UpstreamError("%s %s failed: %s" % (method, url, ex))
    if resp.status_code not in (200, 201):
        raise UpstreamError("%s %s returned HTTP %d" % (method, url, resp.status_code))
    return resp


def get_req(url, param=None, header=None):
    return _request("GET", url, params=param, headers=header)


def post_req(url, data=None, json=None, header=None):
    return _request("POST", url, data=data, json=json, headers=header)


def put_req(url, data=None, json=None, header=None):
    return _request("PUT", url, data=data, json=json, headers=header)


def delete_req(url, data=None, header=None):
    return _request("DELETE", url, headers=header)
