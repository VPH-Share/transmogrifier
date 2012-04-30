# -*- coding: utf-8 -*-
import os
import re
from flask import Blueprint, request, current_app, render_template, make_response
from ..helpers import secure_filename
from . import serialise, allowed_file
from .errors import error_response
from .utils.fileio import joinpath, download, process_file
from .utils.lobcder import put_lob_file

api_identify = Blueprint('identify', __name__, template_folder='.')


@api_identify.route('/v1', methods=['OPTIONS'])
def options_api():
    res = make_response(render_template("spec/api.json"))
    res.mimetype = serialise['json']['mimetype']
    return res


@api_identify.route('/v1/identify', methods=['OPTIONS'])
def options_identify():
    res = make_response(render_template("spec/identify.json"))
    res.mimetype = serialise['json']['mimetype']
    return res


@api_identify.route('/v1/identify', defaults={'format': 'json'}, methods=['GET'])
@api_identify.route('/v1/identify.<format>', methods=['GET'])
def get_identify(format):
    '''Wrapper for GraphicsMagick "gm identify -verbose"'''
    # Enforces a response serialisation format, xml|json. Defaults to json
    fmt_arg = request.values.get('format', '')
    if fmt_arg != '':
        format = request.values.get('format', 'json')

    if format not in serialise.keys():
        err_msg = {"client_error": "Format specified must be json|xml."}
        return error_response(400, err_msg)

    # TODO: Implement fields filter
    # filtered_dict = { field: original_dict[field] for field in field_keys }
    # Process source url
    src = request.values.get('src', '')
    if len(src):
        # # Load file from specified LOBCDER source path
        if src.startswith(current_app.config['LOBCDER_DAV_ROOT']):
            fname = src.split(current_app.config['LOBCDER_DAV_ROOT'])[-1]
            f = joinpath(current_app.config['LOBCDER_FOLDER'], secure_filename(fname))
            # Check if we are still rooted to LOBCDER_FOLDER mount point
            if f.startswith(current_app.config['LOBCDER_FOLDER']):
                if os.path.isfile(f):
                    # TODO fix verbose json error
                    if not allowed_file(fname):
                        err_msg = {"client_error": "File type not supported."}
                        return error_response(400, err_msg)
                    res = process_file('gm identify -verbose %s' % f, identify_to_dict)
                    # res = process_file('gm identify %s' % f)
                    response = make_response(serialise[format]['wrapper'](res))
                    response.mimetype = serialise[format]['mimetype']
                    return response
                else:
                    err_msg = {"server_error": "Destination file not found."}
                    return error_response(502, err_msg)
            else:
                err_msg = {"client_error": "Insecure file path specified."}
                return error_response(403, err_msg)
        else:
            # Download file from external source url
            fname, code, err_msg = download(src, current_app.config['UPLOAD_FOLDER'])
            if err_msg:
                return error_response(code, err_msg)
            if not allowed_file(fname):
                err_msg = {"client_error": "File type not supported."}
                return error_response(400, err_msg)
            res = process_file('gm identify -verbose %s' % fname, identify_to_dict)
            # res = process_file('gm identify %s' % fname)
            response = make_response(serialise[format]['wrapper'](res))
            response.mimetype = serialise[format]['mimetype']
            return response
    else:
        err_msg = {"client_error": "Source url not specified."}
        return error_response(400, err_msg)


@api_identify.route('/v1/identify', defaults={'format': 'json'}, methods=['POST'])
@api_identify.route('/v1/identify.<format>', methods=['POST'])
def post_identify(format):
    # Enforces a response serialisation format, xml|json. Defaults to json
    fmt_arg = request.values.get('format', '')
    if fmt_arg != '':
        format = request.values.get('format', 'json')

    if format not in serialise.keys():
        err_msg = {"client_error": "Format specified must be json|xml."}
        return error_response(400, err_msg)

    if 'file' in request.files:
        f = request.files['file']
        fname = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        # Restricting file mimetypes to prevent XSS
        if not allowed_file(fname):
            err_msg = {"client_error": "File type not supported."}
            return error_response(400, err_msg)
        f.save(fname)
        res = process_file('gm identify -verbose %s' % fname, identify_to_dict)
        # res = process_file('gm identify %s' % fname)
        # Optionally place processed file in LOBCDER destination path
        dest = request.values.get('dest', '')
        if len(dest):
            # err_res = put_lob_file(f, dest)
            err_res = put_lob_file(fname, dest)
            if err_res:
                return err_res
            res['lob-id'] = dest.split(current_app.config['LOBCDER_FOLDER'])[-1]
        response = make_response(serialise[format]['wrapper'](res))
        response.mimetype = serialise[format]['mimetype']
        return response
    else:
        err_msg = {"client_error": "File not posted."}
        return error_response(400, err_msg)


# TODO: Ugly code, but kinda works. Beware, here be dragons!!
def identify_to_dict(data):
    '''Returns a Python dict of the identify response'''
    tree = {}
    nodes = data.split('\n')
    k, v = nodes[0].strip().split(':')
    tree[k] = v.split('/')[-1]

    for i, line in enumerate(nodes[1:]):
        tab = len(re.match(r"\s*", line).group())
        kv = line.split(':')
        if len(kv) == 3:
            kv[1] = kv[1] + ':' + kv[2]
        key = kv[0].strip().replace(' ', '-')
        value = kv[1].strip()
        if tab == 2:
            if value == '':
                tree[key] = {}
            else:
                tree[key] = value
            last2 = key
        if tab == 4:
            if value == '':
                tree[last2][key] = {}
            else:
                tree[last2][key] = value
            last4 = key
        if tab == 6:
            if value == '':
                tree[last2][last4][key] = {}
            else:
                tree[last2][last4][key] = value
            # last6 = key
    return tree
