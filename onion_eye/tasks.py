from flask import current_app
from onion_eye import celery, utils
from onion_eye.config import Config
import requests
import json
import datetime as dt
from urllib.parse import urlparse
from tldextract import extract

celery.conf.beat_schedule = {
    'task-looper': {
        'task': 'onion_eye.tasks.looper',
        'schedule': 600,
    }
}


@celery.task()
def initial_fetch(onion_site):
    url_parse = urlparse(onion_site)
    if url_parse.scheme not in ['http', 'https']:
        pass

    url_tld = extract(onion_site)
    if url_tld.suffix != 'onion':
        pass

    try:
        result = requests.get(
            onion_site,
            proxies=Config.REQUESTS_PROXY,
            verify=False,
            )
    except Exception as e:
        return {'error': True, 'error_stack': e}

    if result.status_code == 200:
        data = {}
        data['site'] = result.url
        data['online'] = True
        data['last_seen_online'] = dt.datetime.now()
        data['last_ping'] = data['last_seen_online']
        data['next_ping'] = data['last_ping'] + dt.timedelta(hours=1)
        url_parse = urlparse(result.url)
        key = "onion_eye:{0}://{1}".format(url_parse.scheme, url_parse.netloc)
        current_app.redis.set(
            key,
            json.dumps(data, default=utils.data_converter))
        return {'site': onion_site, 'success': True}
    else:
        return {'site': onion_site, 'success': False}


@celery.task()
def looper():
    counter = 0
    onion_site_keys = current_app.redis.keys('onion_eye:*')
    for each in onion_site_keys:
        data = json.loads(current_app.redis.get(each))
        next_ping = utils.to_dt(data['next_ping'])
        if next_ping < dt.datetime.now():
            fetch.apply_async((each, data))
            counter += 1
    return {'fetch': counter}


@celery.task()
def fetch(key, data):
    try:
        result = requests.get(
            data['site'],
            proxies=Config.REQUESTS_PROXY,
            verify=False,
            )
    except Exception as e:
        data['online'] = False
        data['next_ping'] = dt.datetime.now() + (
            (utils.to_dt(data['next_ping']) - utils.to_dt(data['last_ping']))
            * 2)
        data['last_ping'] = dt.datetime.now()
        current_app.redis.set(
            key,
            json.dumps(data, default=utils.data_converter)
            )
        return {
            'site': data['site'],
            'online': data['online'],
            'status': 'Error',
            'error_stack': e
            }

    if result.status_code == 200:
        data['online'] = True
        data['last_seen_online'] = dt.datetime.now()
        data['next_ping'] = dt.datetime.now() + \
            dt.timedelta(hours=1)
    else:
        data['online'] = False
        data['next_ping'] = dt.datetime.now() + (
            (utils.to_dt(data['next_ping']) - utils.to_dt(data['last_ping']))
            * 2)
    data['last_ping'] = dt.datetime.now()
    current_app.redis.set(key, json.dumps(data, default=utils.data_converter))
    return {'site': data['site'], 'online': data['online']}


"""
redis schema
onion:<link>

json schema
site: http://.onion:8080
online: true
last_seen_online:
last_ping:
next_ping:
"""
