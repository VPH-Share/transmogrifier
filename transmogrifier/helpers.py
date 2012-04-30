# -*- coding: utf-8 -*-
import re
import gzip
import StringIO
from werkzeug import url_decode
from flask import request

ENV_HEADERS = (
    # 'X-Varnish',
    'X-Request-Start',
    'X-Real-Ip',
    'X-Forwarded-Proto',
    'X-Forwarded-For',
    'X-Forwarded-Protocol',
    'X-Forwarded-Port'
)

_filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-/]')
_windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                     'LPT2', 'LPT3', 'PRN', 'NUL')


def secure_filename(filename):
    """Removes NULL bytes from String"""
    if isinstance(filename, unicode):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('ascii', 'ignore')
    filename = filename.replace("\x00", "")
    return filename


def get_headers(hide_env=True):
    """Returns headers dict from request context."""

    headers = dict(request.headers.items())

    if hide_env and ('show_env' not in request.args):
        for key in ENV_HEADERS:
            try:
                del headers[key]
            except KeyError:
                pass


def module_exists(module_name):
    try:
        __import__(module_name, fromlist=[module_name])
    except ImportError:
        return False
    else:
        return True


class StripPathMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e, h)


class MethodRewriteMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if '_method' in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.get('_method')
            if method:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
        return self.app(environ, start_response)

# class MethodRewriteMiddleware(object):
#     """Legacy Browser and HTTP REST Methods Support
#     For HTML form use:
#     <input type="hidden" name="_method" value="OPTIONS" />
#     """
#     HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE',
#                     'HEAD', 'OPTIONS',
#                     'TRACE', 'CONNECT']

#     def __init__(self, app, input_name='_method'):
#         self.app = app
#         self.input_name = input_name

#     def __call__(self, environ, start_response):
#         request = Request(environ)

        if self.input_name in request.form:
            method = request.form[self.input_name].upper()

            if method in self.HTTP_METHODS:
                environ['REQUEST_METHOD'] = method

        return self.app(environ, start_response)


class GzipMiddleware(object):
    def __init__(self, app, compresslevel=9):
        self.app = app
        self.compresslevel = compresslevel

    def __call__(self, environ, start_response):
        if 'gzip' not in environ.get('HTTP_ACCEPT_ENCODING', ''):
            return self.app(environ, start_response)
        if environ['PATH_INFO'][-3:] != '.js' and environ['PATH_INFO'][-4:] != '.css':
            return self.app(environ, start_response)
        buffer = StringIO.StringIO()
        output = gzip.GzipFile(
            mode='wb',
            compresslevel=self.compresslevel,
            fileobj=buffer
        )

        start_response_args = []

        def dummy_start_response(status, headers, exc_info=None):
            start_response_args.append(status)
            start_response_args.append(headers)
            start_response_args.append(exc_info)
            return output.write

        app_iter = self.app(environ, dummy_start_response)
        for line in app_iter:
            output.write(line)
        if hasattr(app_iter, 'close'):
            app_iter.close()
        output.close()
        buffer.seek(0)
        result = buffer.getvalue()
        headers = []
        for name, value in start_response_args[1]:
            if name.lower() != 'content-length':
                headers.append((name, value))
        headers.append(('Content-Length', str(len(result))))
        headers.append(('Content-Encoding', 'gzip'))
        start_response(start_response_args[0], headers, start_response_args[2])
        buffer.close()
        return [result]


class NginxReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

sample_ngix_config = """
server {
    listen 80;
    server_name www.example.com;
    rewrite ^/(.*) https://example.com/$1 permanent;
}

server {
    listen 80;
    server_name example.com;
    rewrite ^/(.*) https://example.com/$1 permanent;
}

server {
    listen 443;

    ssl on;
    ssl_certificate /etc/ssl/certs/example_com.crt;
    ssl_certificate_key /etc/ssl/private/example_com.key;

    server_name example.com;
    access_log /home/matt/log/example.com/access.log;
    error_log /home/matt/log/example.com/error.log;

    location / {
        # checks for static files; if not found, proxy to app
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;

        proxy_pass http://app_server;
    }

}
"""