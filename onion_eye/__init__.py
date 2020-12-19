import os
from flask import Flask
from celery import Celery
import redis

from .config import Config

celery = Celery(
    __name__,
    broker=Config.BROKER_URL,
    backend=Config.RESULT_BACKEND
    )


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.redis = redis.from_url(
        app.config['REDIS_URL'],
        decode_responses=True)

    from .web.views import views as web_views_bp
    app.register_blueprint(web_views_bp)

    return app
