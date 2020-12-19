import os


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        default='dev')
    REDIS_URL = os.environ.get(
        'REDIS_URL',
        default='redis://localhost:6379')
    BROKER_URL = os.getenv(
        'BROKER_URL',
        default='redis://localhost:6379')
    RESULT_BACKEND = os.environ.get(
        'RESULT_BACKEND',
        default='redis://localhost:6379')
    TOR_PROXY = os.environ.get(
        'TOR_PROXY',
        default='socks5h://localhost:9050')
    REQUESTS_PROXY = {
        'http': TOR_PROXY,
        'https': TOR_PROXY
        }

    @staticmethod
    def init_app(app):
        pass
