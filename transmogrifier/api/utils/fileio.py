import os
import urlparse
import urllib2
import shutil
from cliutils import Process
from werkzeug import secure_filename
from werkzeug.security import safe_join
from flask import current_app
from ..errors import error_response


def joinpath(base, path):
    '''Shorthand for returning a normalised & joined path'''
    return os.path.normpath(safe_join(base, path))


def download(url, base_path):
    '''Smart downloader which handles images that follows redirection'''
    def getFileName(url, openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(), ''),
                openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename:
                    return filename
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    code = 200
    err_msg = None
    try:
        # Spoof 'User-Agent' else we may get a 403. Yes, I'm not playing nice.
        h = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20120405 Firefox/14.0a1'}
        r = urllib2.urlopen(urllib2.Request(url, headers=h))
    except urllib2.HTTPError, e:
        code = 502
        err_msg = {"server_error": "Couldn't fullfill the request. %s" % e.msg}
        return '', code, err_msg
    except urllib2.URLError, e:
        code = 502
        err_msg = {"server_error": "Source url unreachable. %s" % e.reason}
        return '', code, err_msg
    try:
        fileName = secure_filename(getFileName(url, r))
        fname = joinpath(current_app.config['UPLOAD_FOLDER'], fileName).strip()
        with open(fname, 'wb') as f:
            shutil.copyfileobj(r, f)
    finally:
        r.close()
    return fname, code, err_msg


def process_file(cmd, wrap_func=lambda x: {'response': x}):
    '''Process file via command and wrap the response via wrap_func'''
    p = Process('%s' % cmd)
    if p.retcode == 0:
        res = wrap_func(p.stdout)
        return res
    else:
        # Handle File Access error
        err = p.stderr.split(':')[-1].split('(')[0].strip()
        err_msg = {"server_error": err}
        return error_response(500, err_msg)
