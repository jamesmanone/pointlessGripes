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

def content_escape(content):
    content = str(content)
    content = content.replace('&', '&amp;')
    content = content.replace('<', '&lt;')
    content = content.replace('>', '&gt;')
    content = content.replace('"', '&quot;')
    content = content.replace('&lt;b&gt;', '<b>')
    content = content.replace('&lt;/b&gt;', '</b>')
    content = content.replace('&lt;strong&gt;', '<strong>')
    content = content.replace('&lt;/strong&gt;', '</strong>')
    content = content.replace('&lt;em&gt;', '<em>')
    content = content.replace('&lt;/em&gt;', '</em>')
    content = content.replace('&lt;br&gt;', '<br>')
    content = content.replace('&lt;code&gt;', '<code>')
    content = content.replace('&lt;/code&gt;', '</code>')
    content = content.replace('&lt;u&gt;', '<u>')
    content = content.replace('&lt;/u&gt;', '</u>')
    content = content.replace('\n', '<br>')
    content = content.replace('  ', '&nbsp;&nbsp;')
    return content

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
    upvote = db.IntegerProperty(required = True)

    @classmethod
    def postquery(cls, start, limit):
        posts = Post.all().order('-created').fetch(limit = limit,
        offset = start)
        return posts

class Comment(db.Model):
    user = db.StringProperty(required = True)
    comment = db.TextProperty(required = True)
    post_id = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Upvote(db.Model):
    user = db.StringProperty(required = True)
    post_id = db.IntegerProperty(required = True)


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
        if cookie and check_cookie_hash(cookie):
            user = int(cookie.split('|')[0])
            self.user = User.get_by_id(user)
        else:
            self.user = False


class MainHandler(Handler):
    def get(self):
        posts = Post.all().order('-created')
        print posts
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
            return

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
            content = content_escape(content)
            post = Post(subject = subject, content = content,\
            user = self.user.username, upvote = 0)
            post.put()
            self.redirect('/permalink/{0}'.format(post.key().id()))


class EditHandler(Handler):
    def get(self, post_id):
        post =  Post.get_by_id(int(post_id))

        self.render('editpost.html', subject = post.subject,
            content = post.content)

    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        subject = self.request.get('subject')
        content = self.request.get('content')
        if not self.user:
            self.redirect('/login')
        elif self.user.username != post.user:
            self.error(401)
            return
        elif not subject or not content:
            self.render('editpost.html', post = post, subject = subject, content = content, error = 'We need a subject and some content')
        else:
            post.subject = subject
            post.content = content_escape(content)
            post.put()
            self.redirect('/permalink/{0}'.format(post_id))


class CommentHandler(Handler):

    def get(self, post_id):
        comments = Comment.all().filter('post_id =', int(post_id)).order('created')
        self.render('comments.html', comments = comments)
    def post(self, post_id):

        comment = self.request.get('comment')
        if not self.user:
            self.error(401)
            return
        elif not comment:
            self.write('Say something!')
        else:
            comment = Comment(user = self.user.username, comment = comment, post_id = int(post_id))
            comment.put()


class UpvoteHandler(Handler):

    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if self.user:
            upvote = Upvote.all().filter('user = ', self.user).filter('post_id = ', int(post_id))
            if post.user == self.user.username:
                self.write('You can\'t vote up your own post')
            elif upvote:
                self.write('One per customer, pal')
            else:
                post.upvote+=1
                post.put()
                upvote = Upvote(user = self.user.username, post_id = post.key().id())
                upvote.put()
        else:
            self.error(401)




class DeleteHandler(Handler):

    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not self.user:
            self.redirect('/login')
        elif self.user.username != post.user:
            self.render('permalink.html', error = 'You cannot delete someone elses post')
        else:
            post.delete()



class LogoutHandler(Handler):
    def get(self):
        self.response.headers.add_header("Set-Cookie", 'user=; Path=/')
        self.redirect('/')


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



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler),
    ('/permalink/([0-9]+)', PermalinkHandler),
    ('/logout', LogoutHandler),
    ('/welcome', WelcomeHandler),
    ('/newpost', NewPostHandler),
    ('/editpost/([0-9]+)', EditHandler),
    ('/delete/([0-9]+)', DeleteHandler),
    ('/comment/([0-9]+)', CommentHandler),
    ('/upvote/([0-9]+)', UpvoteHandler)
], debug=True)
