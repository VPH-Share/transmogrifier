# -*- coding: utf-8 -*-

from .helpers import module_exists

if module_exists('pytz.gae') and module_exists('flaskext.babel'):
    from pytz.gae import pytz
    from flaskext.babel import Babel
    babel = Babel()


if module_exists('flaskext.sqlalchemy'):
    from flaskext.sqlalchemy import SQLAlchemy
    db = SQLAlchemy()

if module_exists('flaskext.mail'):
    from flaskext.mail import Mail
    mail = Mail()

if module_exists('flaskext.cache'):
    from flaskext.cache import Cache
    cache = Cache()

if module_exists('flaskext.login'):
    from flaskext.login import LoginManager
    login_manager = LoginManager()

if module_exists('flaskext.debugtoolbar'):
    from flaskext.debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension()
