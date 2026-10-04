"""Optional shared storage for live graph views and reports (Upstash Redis REST API).

Serverless instances do not share /tmp, so a graph or report saved by one instance is invisible to
the next. When KV_REST_API_URL/KV_REST_API_TOKEN (Vercel's Upstash integration) or
UPSTASH_REDIS_REST_URL/UPSTASH_REDIS_REST_TOKEN are set, records are mirrored there. Failures never
break a request: the local copy still works, and reads fall back to it.
"""
import json
import os
from urllib.parse import urlparse

from atlas.integrations import secure_request


def _config():
    url = os.environ.get('KV_REST_API_URL') or os.environ.get('UPSTASH_REDIS_REST_URL')
    token = os.environ.get('KV_REST_API_TOKEN') or os.environ.get('UPSTASH_REDIS_REST_TOKEN')
    return (url.rstrip('/'), token) if url and token else (None, None)


def enabled():
    return _config()[0] is not None


def _command(*args):
    url, token = _config()
    response = secure_request(url, list(args), {'Authorization': 'Bearer ' + token}, {urlparse(url).hostname})
    if 'error' in response:
        raise ValueError('KV error')
    return response.get('result')


def put(key, value, ttl_seconds):
    if not enabled():
        return False
    try:
        return _command('SET', 'asterisk:' + key, json.dumps(value, ensure_ascii=False), 'EX', str(ttl_seconds)) == 'OK'
    except Exception:
        return False


def get(key):
    if not enabled():
        return None
    try:
        value = _command('GET', 'asterisk:' + key)
        return json.loads(value) if value else None
    except Exception:
        return None
