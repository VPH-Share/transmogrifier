from flask import Blueprint, render_template, make_response
docs = Blueprint('docs', __name__, static_folder='static', template_folder='templates')


@docs.route('/')
@docs.route('/index.html')
def about():
    return render_template('index.html')


@docs.route('/docs')
@docs.route('/docs.html')
def index():
    return render_template('docs.html')


# TODO: Use SharedDataMiddleWare for static files. Too lazy to set it up
@docs.route('/robots.txt')
def robots():
    res = make_response(render_template('robots.txt'))
    res.mimetype = 'text/plain'
    return res


@docs.route('/humans.txt')
def humans():
    res = make_response(render_template('humans.txt'))
    res.mimetype = 'text/plain'
    return res


@docs.route('/crossdomain.xml')
def crossdomain():
    res = make_response(render_template('crossdomain.xml'))
    res.mimetype = 'application/xml'
    return res
