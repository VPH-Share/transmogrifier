# -*- coding: utf-8 -*-
from transmogrifier import create_app
from transmogrifier.settings import DevConfig
application = create_app(config=DevConfig)

if __name__ == "__main__":
    application.run(**application.config['WERKZEUG_OPTS'])
