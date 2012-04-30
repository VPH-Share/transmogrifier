# -*- coding: utf-8 -*-
import os

SITE_NAME = 'transmogrifier'


class BaseConfig(object):
    """Base Configuration Settings"""
    SITE_NAME = 'transmogrifier'
    SITE_AUTHOR = 'Susheel Varma (susheel.varma@sheffield.ac.uk)'
    SITE_DESCRIPTION = 'RESTful GraphicsMagick Wrapper'
    SITE_KEYWORDS = 'image, transformation, graphicsmagick, wrapper'
    SITE_ADMINS = ['Susheel Varma (susheel.varma@sheffield.ac.uk)']

    # Un-comment if you want to run without gunicorn or gevent concurrency
    LISTEN_HOST = os.environ.get('HOST', '0.0.0.0')
    LISTEN_PORT = os.environ.get('PORT', 5000)
    # If users want to pass specific werkzeug options
    WERKZEUG_OPTS = {'host': LISTEN_HOST, 'port': LISTEN_PORT}

    # When behind a load balancer, set CANONICAL_NAME and CANONICAL_PORT to the
    # value contained in Host headers (e.g. 'www.example.org' and 80)
    # CANONICAL_NAME = '127.0.0.1'
    # CANONICAL_PORT = 8080
    # CANONICAL_SERVER = CANONICAL_NAME+':'+str(CANONICAL_PORT)

    SECRET_KEY = 'secret'
    MAX_CONTENT_LENGTH = 12 * 1024 * 1024  # 12Mb upload limit


class DefaultConfig(BaseConfig):
    '''Default Configuration Settings'''

    # Application specific configurations
    UPLOAD_FOLDER = '/var/vphapp/tmp'
    # LOBCDER configuration
    LOBCDER_DAV_ROOT = 'lob://'
    LOBCDER_FOLDER = '/media/lobcder/public'

    ACCEPT_LANGUAGES = ['en']
    BABEL_DEFAULT_LOCALE = 'en'

    GANALYTICS = 'UAXXXXXXXX1'


class DevConfig(DefaultConfig):
    DEBUG = True
    PROFILE_LOG = '/tmp/profiler.log'


class TestConfig(DevConfig):
    TESTING = True


class ProdConfig(DefaultConfig):
    LISTEN_HOST = os.environ.get('HOST', '0.0.0.0')
    LISTEN_PORT = os.environ.get('PORT', 80)

    # Logging
    DEBUG_LOG = '/var/log/' + SITE_NAME.replace(' ', '_') + '/debug.log'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'joebloggs')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'j0e8l0gg5')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    NGINX_REVERSE_PROXIED = True
    USE_X_SENDFILE = True
