# -*- coding: utf-8 -*-
import os
import shutil
from flask import Blueprint, request, make_response, render_template, g, current_app, Response
from flask import send_file
from ..helpers import secure_filename
from . import ALLOWED_EXTENSIONS, allowed_file
from .errors import error_response
from .utils.fileio import joinpath, process_file, download
from .utils.lobcder import put_lob_file

api_convert = Blueprint('convert', __name__, template_folder='.')

PARAMETERS = ['flip', 'format', 'resize', 'rotate', 'thumbnail']


@api_convert.route('/v1/convert', methods=['OPTIONS'])
def options_convert():
    res = make_response(render_template("spec/convert.json"))
    res.mimetype = 'application/json'
    return res


@api_convert.route('/v1/convert', methods=['GET'])
def get_convert():
    src = request.values.get('src')
    cmds = g.cmds

    if src:
        # # Load file from specified LOBCDER source path
        if src.startswith(current_app.config['LOBCDER_DAV_ROOT']):
            fname = src.split(current_app.config['LOBCDER_DAV_ROOT'])[-1]
            fsrc = joinpath(current_app.config['LOBCDER_FOLDER'], fname)
            # Check if we are still rooted to LOBCDER_FOLDER mount point
            if fsrc.startswith(current_app.config['LOBCDER_FOLDER']):
                if os.path.isfile(fsrc):
                    if not allowed_file(fname):
                        err_msg = {"client_error": "File type not supported."}
                        return error_response(400, err_msg)
                    # Copy file to upload folder
                    ftmp = joinpath(current_app.config['UPLOAD_FOLDER'], secure_filename(os.path.basename(fsrc)))
                    print fsrc, ftmp
                    shutil.copy2(fsrc, ftmp)
                    # Process file
                    res = process_file("%s %s" % (cmds, ftmp))
                    if isinstance(res, Response):
                        return res
                    else:
                        if 'format' in g.params:
                            fret = ftmp.rsplit('.', 1)[0] + '.' + g.params['format']
                        else:
                            fret = ftmp
                        return send_file(fret)
                else:
                    err_msg = {"server_error": "Destination file not found.",
                               "more_info": "/#convert"}
                    return error_response(502, err_msg)
            else:
                err_msg = {"client_error": "Insecure file path specified.",
                           "more_info": "/#convert"}
                return error_response(403, err_msg)
        else:
            # Download file from external source url
            fname, code, err_msg = download(src, current_app.config['UPLOAD_FOLDER'])
            if err_msg:
                return error_response(code, err_msg)
            res = process_file("%s %s" % (cmds, fname))
            if isinstance(res, Response):
                return res
            else:
                if 'format' in g.params:
                    fret = fname.rsplit('.', 1)[0] + '.' + g.params['format']
                else:
                    fret = fname
                return send_file(fret)


@api_convert.route('/v1/convert', methods=['POST'])
def post_convert():
    cmds = g.cmds

    if 'file' in request.files:
        f = request.files['file']
        fname = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        # Restricting file mimetypes to prevent XSS
        if not allowed_file(fname):
            err_msg = {"client_error": "File type not supported.",
                       "more_info": "/#convert"}
            return error_response(400, err_msg)
        f.save(fname)
        res = process_file('%s %s' % (cmds, fname))
        if isinstance(res, Response):
            return res
        else:
            # Optionally place processed file in LOBCDER destination path
            dest = request.values.get('dest', '')
            if len(dest):
                # err_res = put_lob_file(f, dest)
                err_res = put_lob_file(fname, dest)
                if err_res:
                    return err_res
                # else
                if 'format' in g.params:
                    fret = fname.rsplit('.', 1)[0] + '.' + g.params['format']
                else:
                    fret = fname
                return send_file(fret)
            else:
                return send_file(fname)
    else:
        err_msg = {"client_error": "File not posted.",
                   "more_info": "/#convert"}
        return error_response(400, err_msg)


@api_convert.before_request
def process_params():
    '''Basic checks and process submitted parameters'''
    # TODO: Handle User delegated credentials

    # Handle required GET and POST parameters (src, file)
    if request.method == 'GET' and not request.values.get('src'):
        err_msg = {"client_error": "Source url not specified.",
                   "more_info": "/#convert"}
        return error_response(400, err_msg)
    elif request.method == 'POST' and not request.files.get('file'):
        err_msg = {"client_error": "File not posted.",
                   "more_info": "/#convert"}
        return error_response(400, err_msg)

    # Build command string by processing parameters
    g.params = {}
    cmds = []
    for k, v in request.values.items():
        if k in PARAMETERS:
            g.params[k] = v
            if k == 'flip':
                if v.upper() == 'H':
                    cmds.append('-flop')
                elif v.upper() == 'V':
                    cmds.append('-flip')
                elif v.upper() == '':
                    pass
                else:
                    err_msg = {"client_error": "'flip' param must be H or V.",
                               "more_info": "/#convert"}
                    return error_response(400, err_msg)
            elif k == 'format':
                if str(v).lower() in ALLOWED_EXTENSIONS:
                    cmds.append('-format %s' % str(v))
                    g.format = v
                elif str(v).lower() == '':
                    pass
                else:
                    err_msg = {"client_error": "Illegal 'format' type specified.",
                               "more_info": "/#convert"}
                    return error_response(400, err_msg)
            elif k == 'resize':
                splits = v.split('x')
                if len(splits) == 2 and (splits[0].isdigit() and splits[1].isdigit()):
                    cmds.append('-resize %s' % str(v))
                elif v == '':
                    pass
                else:
                    err_msg = {"client_error": "'resize' param must be of format WxH.",
                               "more_info": "/#convert"}
                    return error_response(400, err_msg)
            elif k == 'rotate':
                if v.isdigit() or v.isnumeric():
                    cmds.append(' -rotate %s' % str(v))
                elif v == '':
                    pass
                else:
                    err_msg = {"client_error": "'rotate' param must be a number.",
                               "more_info": "/#convert"}
                    return error_response(400, err_msg)
            elif k == 'thumbnail':
                if len(v.split('x')) == 2:
                    cmds.append(' -thumbnail %s ' % str(v))
                elif v == '':
                    pass
                else:
                    err_msg = {"client_error": "'thumbnail' param must be of format WxH.",
                               "more_info": "/#convert"}
                    return error_response(400, err_msg)
    g.cmds = 'gm mogrify ' + ' '.join(cmds)
