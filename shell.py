# -*- coding: utf-8 -*-
from transmogrifier import create_app
application = create_app()
ctx = application.test_request_context()
ctx.push()
