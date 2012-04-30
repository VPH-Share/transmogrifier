# -*- coding: utf-8 -*-
import os
from flask import Flask, request, render_template, send_from_directory

from .settings import SITE_NAME, DefaultConfig
# from .extensions import toolbar
# from .extensions import babel, cache, db, mail
# from .extensions import login_manager
from .frontend.docs import docs
from .api.errors import api_error
from .api.identify import api_identify
from .api.convert import api_convert

__all__ = ['create_app']

# Default Blueprints
BLUEPRINTS = [api_error, docs, api_identify, api_convert]


def create_app(name=SITE_NAME, config=DefaultConfig, blueprints=BLUEPRINTS):
    '''Application Factory that returns a pre-configured Flask app'''

    app = Flask(name, static_path="/%(SITE_NAME)s/frontend/static")

    # Load settings
    configure_app(app, config)
    configure_wsgi_apps(app)
    configure_hooks(app)
    configure_blueprints(app, blueprints)
    # configure_extensions(app)
    # configure_logging(app)
    configure_filters(app)
    # configure_error_handlers(app)

    # Load testing stubs
    if app.config['TESTING']:
        from api.stubs import api_stubs
        app.register_blueprint(api_stubs)

    return app


def configure_app(app, config=None):
    '''Load application settings'''
    app.config.from_object(DefaultConfig)
    if config is not None:
        app.config.from_object(config)
    # Environment variable for settings override
    app.config.from_envvar('APPLICATION_SETTINGS', silent=True)


def configure_wsgi_apps(app):
    '''Load and initialise wsgi middleware fixers'''
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

    from .helpers import MethodRewriteMiddleware
    app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)

    from .helpers import StripPathMiddleware
    app.wsgi_app = StripPathMiddleware(app.wsgi_app)

    from .helpers import GzipMiddleware
    app.wsgi_app = GzipMiddleware(app.wsgi_app)

    if app.config.get('NGINX_REVERSE_PROXIED', None):
        from .helpers import NginxReverseProxied
        app.wsgi_app = NginxReverseProxied(app.wsgi_app)

    # if app.config['DEBUG'] or app.config['TESTING']:
        # import sys
        # from werkzeug.contrib.profiler import ProfilerMiddleware, MergeStream
        # from werkzeug.contrib.lint import LintMiddleware
        # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, \
        #     MergeStream(sys.stderr, open(app.config['PROFILE_LOG'], 'w')))
        # app.wsgi_app = LintMiddleware(app.wsgi_app)


def configure_hooks(app):
    '''Request / Response hooks'''
    # TODO: Handle ?raise_error=404 stub. See http://flask.pocoo.org/snippets/83/
    @app.before_request
    def before_request():
        from flask import g
        if request.values.get('surpress_error') == "True":
            g.surpress_error = True

    @app.after_request
    def after_request(response):
        from flask import g, make_response
        if hasattr(g, 'surpress_error') and g.surpress_error:
            if response.staus_code != 200:
                return make_response((response), 200)
        else:
            return response

    # from flask import session, abort
    # @app.before_request
    # def csrf_protect():
    #     if request.method == "POST":
    #         token = session.pop('_csrf_token', None)
    #         if not token or token != request.form.get('_csrf_token'):
    #             abort(403)

    # def generate_csrf_token():
    #     '''Generates a random CSRF token
    #        Use <input type=hidden name=_csrf_token value="{{ csrf_token() }}">
    #        within jinja template
    #     '''
    #     import M2Crypto
    #     if '_csrf_token' not in session:
    #         session['_csrf_token'] = M2Crypto.m2.rand_bytes(24).encode('base64').rstrip()
    #     return session['_csrf_token']
    # app.jinja_env.globals['csrf_token'] = generate_csrf_token


def configure_blueprints(app, blueprints):
    '''Configiure Blueprints'''
    for bp in blueprints:
        app.register_blueprint(bp)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'frontend/static/ico'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')


def configure_extensions(app):
    # Configure babel extension
    babel.init_app(app)

    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)

    # Configure Caching
    cache.init_app(app)

    # Configure SQLAlchemy
    db.init_app(app)

    # Configure DebugToolbar
    toolbar.init_app(app)

    # # Configure login manager
    # login_manager.login_view = 'frontend.login'
    # login_manager.refresh_view = 'frontend.reauth'

    # @login_manager.user_loader
    # def load_user(id):
    #     return User.query.get(int(id))
    # login_manager.setup_app(app)

    # if app.config['DEBUG']:
    #     toolbar = toolbar.init_app(app)


def configure_logging(app):
    '''Setup file(info) and email(error) logging'''
    # Return if in debug or testing mode
    if app.debug or app.testing:
        return

    import logging
    from logging.handlers import RotatingFileHandler, SMTPHandler

    # Set logging level to info
    app.logger.setLevel(logging.INFO)

    # Rotating File loggiing for (info) level
    debug_log = os.path.join(app.root_path, app.config['DEBUG_LOG'])
    file_handler = RotatingFileHandler(debug_log, maxBytes=100000, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(processName)s\t | %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(file_handler)

    # Mail logging haldler for (error) level
    mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['MAIL_USERNAME'],
                               app.config['SITE_ADMINS'],
                               'O_ops... %s failed!' % app.config['SITE_NAME'],
                               (app.config['MAIL_USERNAME'],
                                app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(processName)s\t | %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(mail_handler)


def configure_filters(app):
    from filters import reverse_filter, pretty_date_filter, number_format
    app.jinja_env.filters['reverse'] = reverse_filter
    app.jinja_env.filters['pretty_date'] = pretty_date_filter
    app.jinja_env.filters['number_format'] = number_format


def configure_error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/error.html"), 404
