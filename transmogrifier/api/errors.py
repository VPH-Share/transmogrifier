# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, make_response, jsonify, current_app
from . import serialise

api_error = Blueprint('error', __name__)


# TOOD: Maybe better handling it using http://flask.pocoo.org/snippets/15/
@api_error.route('/error/<code>', defaults={'format': 'json'}, methods=['GET'])
@api_error.route('/error/<int:code>.<format>', methods=['GET'])
def status_code(code, format):
    # Enforces handling of HTTP Client and Server errors
    error_code = str(code)
    if error_code not in error_codes.keys():
        return error_response(404)

    # Enforces a response serialisation format, xml|json. Defaults to json
    # TODO: html format
    if format not in serialise.keys():
        err_msg = {"client_Error": "Format specified must be json|xml.",
                   "more_info": "/#errors"}
        return error_response(400, err_msg)
    else:
        return error_response(int(code), format=format)


def error_response(status_code, data=None, headers=None, format=None, template=None, log_error=False):
    '''Returns an error response using supplied data'''
    if not data:
        data = {}

    # TODO: Use werkzeug default_exceptions and HTTPException
    data['http_status_code'] = status_code
    data['http_status_info'] = error_codes[str(status_code)]

    if template:
        res = make_response(render_template(template, data))
        res.mimetype = 'text/html'
    elif format:
        res = make_response(serialise[format]['wrapper'](data))
        res.mimetype = serialise[format]['mimetype']
    else:
        res = make_response(jsonify(data))
        res.mimetype = serialise['json']['mimetype']

    # # Legacy clients may not handle HTTP errors properly
    # if hasattr(g, 'surpress_error') and g.surpress_error:
    #     res.status_code = 200
    # else:
    #     res.status_code = status_code
    res.status_code = status_code

    if headers:
        res.headers = headers
    if log_error:
        current_app.logger.critical(data)
    return res


error_codes = {

    "400": "Bad Request",
    "401": "Authorization Required",
    "402": "Payment Required",
    "403": "Forbidden",
    "404": "Not Found",
    "405": "Method Not Allowed",
    "406": "Not Acceptable",
    "407": "Proxy Authentication Required",
    "408": "Request Time-out",
    "409": "Conflict",
    "410": "Gone",
    "411": "Length Required",
    "412": "Precondition Failed",
    "413": "Request Entity Too Large",
    "414": "Request-URI Too Large",
    "415": "Unsupported Media Type",
    "416": "Requested Range Not Satisfiable",
    "417": "Expectation Failed",
    "418": "I'm A Teapot",
    "422": "Unprocessable Entity",
    "423": "Locked",
    "424": "Failed Dependency",
    "426": "Upgrade Required",

    "500": "Internal Server Error",
    "501": "Method Not Implemented",
    "502": "Bad Gateway",
    "503": "Service Temporarily Unavailable",
    "504": "Gateway Time-out",
    "505": "HTTP Version Not Supported",
    "506": "Variant Also Negotiates",
    "507": "Insufficient Storage",
    "510": "Not Extended"
}
