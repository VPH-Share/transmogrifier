# -*- coding: utf-8 -*-
from flask import jsonify
from dict2xml import dict2xml


def xmlify(data):
    return '<?xml version="1.0" encoding="UTF-8" ?>\n' \
            + dict2xml(data, wrap='response')

serialise = {
    'json': {
        'wrapper': jsonify,
        'mimetype': 'application/json'
    },
    'xml': {
        'wrapper': xmlify,
        'mimetype': 'application/xml'
    },
    # 'html': {
    #     'wrapper': htmlify,  # TODO: Implement dict2html
    #     'mimetype': 'text/html'
    # }
}

ALLOWED_EXTENSIONS = set(['jpg', 'jpe', 'jpeg', 'png', 'svg', 'bmp', 'tif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
