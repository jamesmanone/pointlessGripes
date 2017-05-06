import json
import os
import webapp2
import jinja2
import models
import utls
from functools import wraps


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        '''Sends data to user'''
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        '''Takes variables and a template as input. Replaces placeholder
        tags in the template
        '''
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        '''helper function. Takes a template and variables, replaces
        placeholders with variables, and sends result to client
        '''
        self.write(self.render_str(template, **kw))

    def set_cookie(self, key):
        '''Makes and sets a cookie
        '''
        self.response.headers.add_header(
            'Set-Cookie', 'user={0}; Path=/'.format(utls.make_cookie_hash(key)))  # NOQA: E501

    def valid_post(self, post):
        if post:
            return True
        else:
            self.error(404)
            return False

    def owns_post(self, post):
            if post:
                return True
            else:
                obj = {
                       'success': False,
                       'message': 'You can only modify your own posts'
                }
                self.json(obj)
                return False

    def valid_comment(self, comment):
        if comment:
            return True
        else:
            self.error(404)
            return False

    def owns_comment(self, comment):
        if comment.user.key() == self.user.key():
            return True
        else:
            obj = {
                   'success': False,
                   'message': 'You can only delete your own comment'
                   }
            self.json(obj)
            return False

    def logged_in(self, fn, *args, **kwargs):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not self.user:
                self.redirect('/login')
            else:
                fn(*args, **kwargs)
        return wrapper

    def initialize(self, *a, **kw):
        '''Called on every page load. Checks user cookie and establishes
        self.user if client has a valid cookie
        '''
        webapp2.RequestHandler.initialize(self, *a, **kw)
        cookie = self.request.cookies.get('user')
        if cookie and utls.check_cookie_hash(cookie):
            user = int(cookie.split('|')[0])
            self.user = models.User.get_by_id(user)
        else:
            self.user = False

    def json(self, obj):
        '''Takes a dictionary as input. Converts to JSON and send it to the
        client
        '''
        self.response.headers['Content-Type'] = 'application/json'
        self.write(json.dumps(obj))
