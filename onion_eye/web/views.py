from flask import Blueprint, current_app, request, render_template
from onion_eye import tasks
from wtforms import Form, StringField, validators
import json

views = Blueprint('views', __name__)


class OnionForm(Form):
    onion_site = StringField('Onion Site', [validators.URL()])


@views.route("/")
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
    return render_template('list.html', site_list=onion_list)


@views.route("/add", methods=['GET', 'POST'])
def add_page():
    form = OnionForm(request.form)
    if request.method == 'POST' and form.validate():
        onion_site = form.onion_site.data
        task = tasks.initial_fetch.apply_async((onion_site,))
        status = {
            'site': onion_site,
            'id': task.id
        }
        return render_template('add.html', form=form, status=status)
    return render_template('add.html', form=form)


@views.route("/search")
def search_page():
    if request.args.get('q'):
        query = request.args.get('q')
        result = current_app.redis.keys(
            'onion_eye:*{0}*'.format(query)
            )
        if result:
            result_list = []
            for each in result:
                result_list.append(json.loads(current_app.redis.get(each)))
            return render_template(
                'search.html',
                q=query,
                list=result_list
                )
        else:
            return render_template(
                'search.html',
                q=query
                )
    return render_template('search.html')
