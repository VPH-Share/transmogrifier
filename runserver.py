# -*- coding: utf-8 -*-
from transmogrifier import create_app
from transmogrifier.settings import ProdConfig
application = create_app(config=ProdConfig)

if __name__ == "__main__":
    application.run(**application.config['WERKZEUG_OPTS'])
