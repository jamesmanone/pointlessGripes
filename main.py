import os
import webapp2
import jinja2
# from google.appengine.ext import db
import secret
import hashlib
import hmac
import random
from string import letters
import json
import models


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


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


def hashword_converter(name, password, salt=make_salt()):
    '''converts name + password + ?salt to password hash + salt.
    Gets salt from make_salt() if none provided
    '''
    return '{0}|{1}'.format(
            hashlib.sha256(name + password + salt).hexdigest(), salt)


def password_valid(name, password, password_hash):
    '''Takes username, password, and saved password_hash. Returns true
    if password_hash matches the result of hashing password
    '''
    salt = password_hash.split('|')[1]
    if hashword_converter(name, password, salt) == password_hash:
        return True


def content_escape(content):
    '''Escapes HTML and subsequently unescapes tags that are allowed. also
    converts newlines to <br>
    '''
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


# class User(db.Model):
#     username = db.StringProperty(required=True)
#     password_hash = db.StringProperty(required=True)
#     email = db.StringProperty()
#     upvotes = db.IntegerProperty()
#
#     @classmethod
#     def by_name(cls, name):
#         '''Fetches user from input name. Returns user info
#         '''
#         user = User.all().filter('username =', name).get()
#         print user
#         return user
#
#     @classmethod
#     def login(cls, name, password):
#         '''Validates username and password and, if valid, returns user
#         '''
#         user = cls.by_name(name)
#         if user and password_valid(name, password, user.password_hash):
#             return user
#
#
# class Post(db.Model):
#     subject = db.StringProperty(required=True)
#     content = db.TextProperty(required=True)
#     created = db.DateTimeProperty(auto_now_add=True)
#     last_modified = db.DateTimeProperty(auto_now=True)
#     user = db.StringProperty(required=True)
#     upvote = db.IntegerProperty(required=True)
#
#     @classmethod
#     def postquery(cls, start, limit):
#         posts = Post.all().order('-created').fetch(limit=limit,
#                                                    offset=start)
#         return posts
#
#
# class Comment(db.Model):
#     user = db.StringProperty(required=True)
#     comment = db.TextProperty(required=True)
#     post_id = db.IntegerProperty(required=True)
#     created = db.DateTimeProperty(auto_now_add=True)
#
#
# class Upvote(db.Model):
#     '''This is a log of all upvotes. used to check if
#     someone has already upvoted a post
#     '''
#     user = db.StringProperty(required=True)
#     post_id = db.IntegerProperty(required=True)


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
            'Set-Cookie', 'user={0}; Path=/'.format(make_cookie_hash(key)))

    def initialize(self, *a, **kw):
        '''Called on every page load. Checks user cookie and establishes
        self.user if client has a valid cookie
        '''
        webapp2.RequestHandler.initialize(self, *a, **kw)
        cookie = self.request.cookies.get('user')
        if cookie and check_cookie_hash(cookie):
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


class MainHandler(Handler):  # For /
    def get(self):
        '''Retrieves posts from db and displays them
        '''
        posts = models.Post.all().order('-created')
        if posts:
            if self.user:
                self.render('main.html', posts=posts, user=self.user)
            else:
                self.render('main.html', posts=posts)
        else:
            self.render('main.html')


class PageHandler(Handler):  # For /page/{pagenumber}
    def get(self, pagenumber):
        pagenumber = int(pagenumber)
        start = pagenumber*20 - 20
        end = start + 21
        posts = models.Post.all().order('-created')
        if self.user:
            self.render('page.html', posts=posts[start:end], user=self.user,
                        pagenumber=pagenumber)
        else:
            self.render('page.html', posts=posts[start:end],
                        pagenumber=pagenumber)


class UserHandler(Handler):  # For /user/{username}
    '''Retrieves posts by a specified user and displays them
    '''
    def get(self, user_id):
        posts = models.User.by_name(user_id).posts.order('-created')
        if posts:
            if self.user:
                self.render('user.html', posts=posts, user=self.user,
                            title=user_id)
            else:
                self.render('user.html', posts=posts, title=user_id)
        else:
            self.error(404)


class LoginHandler(Handler):  # For /login
    def get(self):
        '''sends login page if user is not logged in; else, redirects to /
        '''
        if self.user:
            self.redirect('/')
        else:
            self.render('login.html')

    def post(self):
        '''Validates username and password. If valid, sets a cookie and
        redirects to welcome page
        '''
        name = self.request.get('username')
        password = self.request.get('password')

        if name and password:
            user = models.User.by_name(name)
            salt = user.password_hash.split('|')[1]
        else:
            self.render('login.html', username=name,
                        error="All fields required")
            return

        if user and user.password_hash == hashword_converter(name,
                                                             password, salt):
            self.set_cookie(str(user.key().id()))
            self.redirect('/welcome')
        else:
            self.render('login.html', username=name, error="Username\
            or Password incorect")


class SignupHandler(Handler):  # For /signup
    def get(self):
        '''Sends a signup form. If user is already logged in it redirects to /
        '''
        if not self.user:
            self.render('signup.html')
        else:
            self.redirect('/')

    def post(self):
        '''Takes the signup form data, verifies required fields a populated,
        checks for duplicate username or passwords or usernames too short, and
        if no errors created new User in db and logs the user in
        '''
        username = self.request.get('username')
        password = self.request.get('password')
        passcheck = self.request.get('passcheck')
        email = self.request.get('email')

        in_use = models.User.by_name(username)

        if in_use:
            self.render('signup.html', username=username, email=email,
                        error='Username taken')
        elif password != passcheck:
            self.render('signup.html', username=username, email=email,
                        error='Passwords do not match')
        elif len(password) < 6 or len(username) < 6:
            self.render('signup.html', username=username, email=email,
                        error='Username and password must be a minimum \
                        of 6 characters')
        # elif not check_password(password) or not check_username(username):
        #     self.render('signup.html', username=username, email=email,
        #                 error='Usernames and passwords can contain only\
        #                 capital and lowercase letters, numbers, and the\
        #                 special characters @ # $ % ^ & + =')
        else:
            password_hash = hashword_converter(username, password)
            newuser = models.User(username=username,
                                  password_hash=password_hash,
                                  email=email, upvotes=0)
            newuser.put()
            self.set_cookie(str(newuser.key().id()))

            self.redirect('/welcome')


class NewPostHandler(Handler):  # For /newpost
    def get(self):
        '''Sends new post form if user is logged in, else redirects to /login
        '''
        if not self.user:
            self.redirect('/login')
        self.render('newpost.html', user=self.user)

    def post(self):
        '''Takes data from newpost form. If all fields are populated the
        content field will go through a custom escape function that allows
        some formatting html and replaces new lines with <br>. This data is
        passed to the Post constructer to be added to the db. The user is then
        redirected to the post's permalink
        '''
        subject = self.request.get('subject')
        content = self.request.get('content')

        if not self.user:
            self.redirect('/login')
        elif not subject or not content:
            self.render('newpost.html', subject=subject, content=content,
                        error='We need a subject and some content')
        else:
            content = content_escape(content)
            post = models.Post(subject=subject, content=content,
                               user=self.user)
            post.put()
            self.redirect('/permalink/{0}'.format(post.key().id()))


class EditHandler(Handler):  # for /editpost
    def get(self, post_id):
        '''Sends a form to allow user to edit a post
        '''
        post = models.Post.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        elif self.user.key() == post.user.key():
            self.render('editpost.html', subject=post.subject,
                        content=post.content, post_id=post_id, user=self.user)
        else:
            self.redirect('/login')

    def post(self, post_id):
        '''Takes data from edit form. Verifies user owns the post, and if so
        updates post in db
        '''
        post = models.Post.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        subject = self.request.get('subject')
        content = self.request.get('content')
        if not self.user:
            self.redirect('/login')
        elif self.user != post.user:
            self.error(401)
            return
        elif not subject or not content:
            self.render('editpost.html', post=post, subject=subject,
                        content=content,
                        error='We need a subject and some content')
        else:
            post.subject = subject
            post.content = content_escape(content)
            post.put()
            self.redirect('/permalink/{0}'.format(post_id))


class CommentHandler(Handler):
    # This is an AJAX handler. Do not navigate here
    def get(self, post_id):
        '''Retrieves comments for post. Sends them to user in JSON
        '''
        post = models.Post.get_by_id(int(post_id))
        comments = post.comments
        obj = {'success': True}
        if comments and self.user:
            obj['result'] = self.render_str('comment.html', comments=comments,
                                            user=self.user)
        elif comments:
            obj['result'] = self.render_str('comment.html', comments=comments)
        self.json(obj)

    def post(self, post_id):
        '''Takes a new comment as input. If user is logged in comment is
        added to db, rendered using jinja, and returned to the user in JSON.
        If error, success: False and an error message is sent to user in JSON.
        '''
        post = models.Post.get_by_id(int(post_id))
        comment = self.request.get('comment')
        if not self.user:
            obj = {
                    'success': False,
                    'message': 'You must be <a href="/login">logged in</a>\
                    to comment',
            }
            self.json(obj)
        else:
            comment = models.Comment(user=self.user, comment=comment,
                                     post=post)
            comment.put()
            print comment.comment
            obj = {
                    'success': True,
                    'result': self.render_str('newcommentresponse.html',
                                              comment=comment)
                    }
            print obj['result']
            self.json(obj)


class UpvoteHandler(Handler):
    # This is an AJAX handler. Do not navigate here
    def post(self, post_id):
        '''If user is logged in and hasn't already upvoted this post this will
        add an upvote to the upvote db and increment the post upvote count by
        1. If successful, success: True, and new upvote count is sent in JSON.
        If user is no logged in or has already upvoted this post success: False
        and error message is sent in JSON
        '''
        post = models.Post.get_by_id(int(post_id))
        if self.user:
            upvote = post.upvotes.filter('user =', self.user).get()
            if post.user == self.user:
                self.response.headers['Content-Type'] = 'application/json'
                obj = {
                        'success': False,
                        'message': 'You cant upvote your own post!'
                        }
                self.write(json.dumps(obj))
            elif upvote:
                self.response.headers['Content-Type'] = 'application/json'
                obj = {
                        'success': False,
                        'message': 'You can\'t upvote again'
                        }
                self.write(json.dumps(obj))
            else:
                upvote = models.Upvote(user=self.user, post=post)
                upvote.put()
                obj = {
                        'success': True,
                        'message': ' ' + str(post.upvote)
                        }
                self.json(obj)
        else:
            self.error(401)


class DeleteHandler(Handler):
    # This is an AJAX handler. Do not navigate here
    def post(self, post_id):
        '''If user is logged in and owns the post; deletes the post and sends
        success: True in JSON. else, sends success: False and an error message
        in JSON. The delete requires no confirmation here. Confirmation is
        handled with confirm() in the javascript front end. Also deletes
        upvotes and comments for this post
        '''
        post = models.Post.get_by_id(int(post_id))
        if not self.user:
            self.redirect('/login')
        elif self.user != post.user:
            self.render('permalink.html',
                        error='You cannot delete someone elses post')
        else:
            post.delete()


class LogoutHandler(Handler):  # For /logout
    def get(self):
        '''Sets cookie to 'user=;' and redirects logged out user to /
        '''
        self.response.headers.add_header("Set-Cookie", 'user=; Path=/')
        self.redirect('/')


class WelcomeHandler(Handler):  # For /welcome
    def get(self):
        '''Sends a simple welcome message when user logs in
        '''
        if self.user:
            self.render('welcome.html', user=self.user)
        else:
            self.redirect('/login')
            # I know this should redirect to /signup, but this follows
            # how most websites work. I hope I'm allowed this license


class PermalinkHandler(Handler):  # For /permalink/{post_id}
    def get(self, post_id):
        '''Gets post id from URL. Retrieves post and sends page with that post
        '''
        post = models.Post.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        self.render('permalink.html', post=post, user=self.user)


class CommentDeleteHandler(Handler):
    # This is an AJAX handler. Do not navigate here
    def post(self, comment_id):
        '''Takes comment ID from URL. If user is logged in and owns the comment
        deletes comment. Responds with success: True in JSON. If error,
        responds with success: False and error message in JSON
        '''
        comment = models.Comment.get_by_id(int(comment_id))
        if not self.user:
            obj = {
                    'success': False,
                    'message': 'You must be <a href="/login">logged in</a> \
                    to do this'
            }
            self.json(obj)
        elif self.user.username != comment.user:
            obj = {
                    'success': False,
                    'message': 'You can only delete your own posts'
            }
            self.json(obj)
        else:
            comment.delete()
            obj = {
                    'success': True
            }
            self.json(obj)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/page/([0-9]+)', PageHandler),
    ('/login', LoginHandler),
    ('/signup', SignupHandler),
    ('/permalink/([0-9]+)', PermalinkHandler),
    ('/logout', LogoutHandler),
    ('/welcome', WelcomeHandler),
    ('/newpost', NewPostHandler),
    ('/editpost/([0-9]+)', EditHandler),
    ('/user/([a-z0-9]+)', UserHandler),
    ('/delete/([0-9]+)', DeleteHandler),
    ('/commentdelete/([0-9]+)', CommentDeleteHandler),
    ('/comments/([0-9]+)', CommentHandler),
    ('/upvote/([0-9]+)', UpvoteHandler)
], debug=True)
