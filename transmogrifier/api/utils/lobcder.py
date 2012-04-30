import os
import shutil
import errno
from ..errors import error_response
from .fileio import joinpath
from flask import current_app

__all__ = ['get_lob_file', 'put_lob_file']


def get_lob_file(fsrc, fdest):
    pass


def put_lob_file(fsrc, fdest):
    '''Store the file to lobceder destination specified'''
    if fdest.startswith(current_app.config['LOBCDER_DAV_ROOT']):
        fdest = joinpath(current_app.config['LOBCDER_FOLDER'], fdest.split(current_app.config['LOBCDER_DAV_ROOT'])[-1])
        # Check if we are still rooted to LOBCDER_FOLDER mount point
        if fdest.startswith(current_app.config['LOBCDER_FOLDER']):
            if not os.path.exists(os.path.dirname(fdest)):
                try:
                    os.makedirs(os.path.dirname(fdest))
                except OSError, e:
                    if e.errno != errno.EEXIST:
                        err_msg = {"server_error": "And the OS survey said: %s." % os.strerror(e.errno)}
                        return error_response(500, err_msg)
        else:
            err_msg = {"client_error": "Insecure file path specified."}
            return error_response(403, err_msg)
        if os.path.isdir(fdest):
            try:
                # Save file to directory
                shutil.copy2(fsrc, joinpath(fdest, fsrc.filename))
                # fsrc.save(joinpath(fdest, fsrc.filename))
            except OSError, e:
                if e.errno != errno.EEXIST:
                    err_msg = {"server_error": "And the OS survey said: %s." % os.strerror(e.errno)}
                    return error_response(500, err_msg)
        else:
            try:
                # Save file to dest filename
                print "saving file" + fdest
                shutil.copy2(fsrc, fdest)
                # fsrc.save(fdest)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    err_msg = {"server_error": "And the OS survey said: %s." % os.strerror(e.errno)}
                    return error_response(500, err_msg)
        return None
    else:
        err_msg = {"client_error": "Destination path must start with %s." % current_app.config['LOBCDER_DAV_ROOT']}
        return error_response(412, err_msg)
