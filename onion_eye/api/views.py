from flask import Blueprint, current_app, request
from onion_eye import tasks, utils
import json

views = Blueprint('api', __name__)


@views.route("/list")
def list_site():
    onion_list = []
    onion_list_keys = current_app.redis.keys(
        'onion_eye:*'
    )
    for each in onion_list_keys:
        onion_list.append(json.loads(current_app.redis.get(
            each
        )))
    return json.dumps(onion_list, default=utils.data_converter)


@views.route("/add", methods=['POST'])
def add_page():
    if request.method == 'POST':
        data = request.get_json()
        print(str(data['site']))
        onion_site = data['site']
        tasks.initial_fetch.apply_async((onion_site,))
        status = {
            'site': onion_site,
        }
        return status


@views.route("/search")
def search_page():
    if request.args.get('q'):
        query = request.args.get('q')
        result = current_app.redis.keys(
            'onion_eye:*{0}*'.format(query)
            )
        result_list = []
        for each in result:
            result_list.append(json.loads(current_app.redis.get(each)))
        return json.dumps(result_list, default=utils.data_converter)
    return json.dumps([])
