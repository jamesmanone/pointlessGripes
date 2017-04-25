import os
import webapp2
import jinja2
from google.appengine.ext import db
import secret
import hashlib
import hmac
import random
from string import letters


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

def make_cookie_hash(user):
    '''Takes user id and returns user id and hashstring for cookie
    '''
    return '{0}|{1}'.format(user, hmac.new(secret.secret, user).hexdigest())

def check_cookie_hash(cookie):
    '''Takes cookie as input, verifies the hash, and returns the user id
    '''
    user = cookie.split('|')[0]
    if cookie == make_cookie_hash(user):
        return user

def make_salt():
    '''Does like morton
    '''
    return ''.join(random.choice(letters) for x in xrange(5))

def hashword_converter(name, password, salt = make_salt()):
    '''converts name + password + ?salt to password hash + salt.
    Gets salt from make_salt() if none provided
    '''
    return '{0}|{1}'.format(
            hashlib.sha256(name + password + salt).hexdigest(), salt)

def password_valid(name, password, password_hash):
    salt = password_hash.split('|')[1]
    if hashword_converter(name, password, salt) == password_hash:
        return True

class User(db.Model):
    username = db.StringProperty(required = True)
    password_hash = db.StringProperty(required = True)
    email = db.StringProperty()
    kudos = db.IntegerProperty()

    @classmethod
    def by_name(cls, name):
        '''Fetches user from input name. Returns user info
        '''
        user = User.all().filter('username = ', name).get()
        return user

    @classmethod
    def by_id(cls, user_id):
        return User.get_by_id(user_id)

    @classmethod
    def login(cls, name, password):
        '''Validates username and password and, if valid, returns user id
        '''
        user = cls.by_name(name)
        if user and password_valid(name, password, user.password_hash):
            return user

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    user = db.StringProperty(required = True)
    kudos = db.IntegerProperty()

    @classmethod
    def postquery(cls, start, limit):

        return cls.all().order('-created').fetch(limit, offset=start)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def hash_user_id(self, user_id):
        return  hmac.new(secret.secret, user_id).hexdigest()

    def set_cookie(self, user_id):
        '''Makes and sets a cookie
        '''
        value = hash_user_id(user_id)
        self.response.headers.add_header(
            'Set-Cookie', 'user={0}; Path=/'.format(make_cookie_hash(user_id)))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        cookie = self.request.cookies.get('user')
        if cookie:
            user_id = check_cookie_hash(cookie)
            self.user = user and User.by_id(int(user_id))
        else:
            user = None




class MainHandler(Handler):
    def get(self):
        posts = Post.postquery(10, 0)
        self.render('main.html', posts = posts)

class LoginHandler(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        name = self.request.get('username')
        password = self.request.get('password')

        user = User.get_by_name(name)
        salt = user.password_hash.split('|')[0]

        if user and user.password_hash == hashword_converter(name, password, salt):
            self.set_cookie(user.key)
            self.redirect('/welcome')
        else:
            self.redirect('/signup')


class SignupHandler(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        passcheck = self.request.get('passcheck')
        email = self.request.get('email')

        if User.by_name('username'):
            self.render('signup.html', username = username, email = email,
            error = 'Username taken')
        elif password != passcheck:
            self.render('signup.html', username = username, email = email,
            error = 'Passwords do not match')
        elif len(password)<6 or len(username)<6:
            self.render('signup.html', username = username, email = email,
            error = 'Username and password must be a minimum of 6 characters')
        else:
            newuser = User(username = username, password_hash = password, email = email,
            kudos = 0)
            newuser.put()

            self.redirect('/welcome')



# class EntryPageHandler(Handler):
#     #STUB!!!
#
# class LogoutHandler(Handler):
#     #STUB!!
#
# class WelcomeHandler(Handler):
#     #STUB!!!

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler),
    # ('/blog/([0-9]+)', EntryPageHandler),
    # ('/logout', LogoutHandler),
    # ('/welcome', WelcomeHandler)
], debug=True)
