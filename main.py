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
        user = User.all().filter('username =', name).get()
        print user
        return user

    @classmethod
    def by_id(cls, user_id):
        return User.get_by_id(user_id)

    @classmethod
    def login(cls, name, password):
        '''Validates username and password and, if valid, returns user
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
        posts = Post.all().order('-created').fetch(limit=10)
        return posts

class Comments(db.Model):
    user = db.StringProperty(required = True)
    comment = db.TextProperty(required = True)
    post_id = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Kudos(db.Model):
    user = db.StringProperty(required = True)
    post_id = db.IntegerProperty(required = True)

    @classmethod
    def get_kudos(cls, post_id):
        q = cls.all().filter('post_id =', post_id).count()
        return q

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_cookie(self, key):
        '''Makes and sets a cookie
        '''
        self.response.headers.add_header(
            'Set-Cookie', 'user={0}; Path=/'.format(make_cookie_hash(key)))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        cookie = self.request.cookies.get('user')
        self.user = None
        if cookie and check_cookie_hash(cookie):
            user = int(cookie.split('|')[0])
            self.user = User.get_by_id(user)


class MainHandler(Handler):
    def get(self):
        posts = Post.postquery(10, 0)
        for post in posts:
            kudos = Kudos.get_kudos(post.key())
            post.kudos = kudos
            post.put()
        if self.user:
            self.render('main.html', posts = posts, user = self.user)
        else:
            self.render('main.html', posts = posts)

class LoginHandler(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        name = self.request.get('username')
        password = self.request.get('password')

        if name and password:
            user = User.by_name(name)
            salt = user.password_hash.split('|')[1]
        else:
            self.render('login.html', username = name, error = "All fields\
            required")

        if user and user.password_hash == hashword_converter(name, password, salt):
            self.set_cookie(str(user.key().id()))
            self.redirect('/welcome')
        else:
            self.render('login.html', username = name, error = "Username\
            or Password incorect")


class SignupHandler(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        passcheck = self.request.get('passcheck')
        email = self.request.get('email')

        in_use = User.by_name(username)

        if in_use:
            self.render('signup.html', username = username, email = email,
            error = 'Username taken')
        elif password != passcheck:
            self.render('signup.html', username = username, email = email,
            error = 'Passwords do not match')
        elif len(password)<6 or len(username)<6:
            self.render('signup.html', username = username, email = email,
            error = 'Username and password must be a minimum of 6 characters')
        else:
            password_hash = hashword_converter(username, password)
            newuser = User(username = username, password_hash = password_hash, email = email,
            kudos = 0)
            newuser.put()
            self.set_cookie(str(newuser.key().id()))

            self.redirect('/welcome')


class NewPostHandler(Handler):
    def get(self):
        if not self.user:
            self.redirect('/login')
        self.render('newpost.html')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if not self.user:
            self.redirect('/login')
        elif not subject or not content:
            self.render('newpost.html', subject = subject, content = content,
            error = 'We need a subject and some content')
        else:
            post = Post(subject = subject, content = content,
            user = self.user.username, kudos = 0)
            post.put()
            self.redirect('/permalink/{0}'.format(post.key().id()))


class EditHandler(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))

        self.render('/editpost.html', subject = post.subject,
            content = post.content)

    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        delete = self.request.get('delete')
        if self.user.username != post.user:
            self.redirect('/login')
        if delete:
            post.delete()
            post.put()
            self.redirect('/deleted')
        else:
            post.subject = self.request.get('subject')
            post.content = self.request.get('content')
            post.put()
            self.redirect('/permalink/{0}'.format(post_id))


class DeletedHandler(Handler):
    def get(self):
        self.render('deleted.html')



class LogoutHandler(Handler):
    def get(self):
        if self.user:
            self.response.headers.add_header("Set-Cookie", 'user=; Path=/')
            self.redirect('/welcome')
    def post(self):
        self.response.headers.add_header("Set-Cookie", value = None)
        self.redirect('/login')


class WelcomeHandler(Handler):
    def get(self):
        posts = Post.all().order('-created').fetch(limit=10)
        self.render('welcome.html', posts = posts, user = self.user)


class PermalinkHandler(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        self.render('permalink.html', post = post, user = self.user)

    def post(self, post_id):
        kudos = self.request.get('kudos')
        delete = self.request.get('delete')
        edit = self.request.get('edit')
        post = Post.get_by_id(int(post_id))

        if not self.user:
            self.redirect('/login')

        if delete and self.user.username == post.user:
            self.redirect('/editpost/{0}'.format(post_id))

        elif kudos and self.user.username != post.user:
            if not Kudos.all().filter("post_id=", post.key().id()).filter("user =", self.user.username):
                kudos = Kudos(user = self.user.username, post_id = post.key().id())
                kudos.put()
                self.redirect('/permalink/{0}'.format(post_id))
            else:
                self.render('permalink.html', user = self.user, post = post, error = 'you already gave kudos.')

        elif edit and self.user.username == post.user:
            self.redirect('/editpost/{0}'.format(post_id))
        else:
            self.redirect('/login')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler),
    ('/permalink/([0-9]+)', PermalinkHandler),
    ('/logout', LogoutHandler),
    ('/welcome', WelcomeHandler),
    ('/newpost', NewPostHandler),
    ('/editpost/([0-9]+)', EditHandler),
    ('/deleted', DeletedHandler)
], debug=True)
