
import webapp2
# from google.appengine.ext import db
import models
import handlers
from handlers import proto


class MainHandler(proto.Handler):  # For /
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


class WelcomeHandler(proto.Handler):  # For /welcome
    def get(self):
        '''Sends a simple welcome message when user logs in
        '''
        if self.user:
            self.render('welcome.html', user=self.user)
        else:
            self.redirect('/login')
            # I know this should redirect to /signup, but this follows
            # how most websites work. I hope I'm allowed this license


class PermalinkHandler(proto.Handler):  # For /permalink/{post_id}
    def get(self, post_id):
        '''Gets post id from URL. Retrieves post and sends page with that post
        '''
        post = models.Post.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        self.render('permalink.html', post=post, user=self.user)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/page/([0-9]+)', handlers.PageHandler),
    ('/login', handlers.LoginHandler),
    ('/signup', handlers.SignupHandler),
    ('/usernamecheck', handlers.UsernameCheck),
    ('/permalink/([0-9]+)', PermalinkHandler),
    ('/onepost/([0-9]+)', handlers.OnepostHandler),
    ('/logout', handlers.LogoutHandler),
    ('/welcome', WelcomeHandler),
    ('/newpost', handlers.NewPostHandler),
    ('/editpost/([0-9]+)', handlers.EditHandler),
    ('/user/([a-z0-9]+)', handlers.UserHandler),
    ('/delete/([0-9]+)', handlers.DeleteHandler),
    ('/commentdelete/([0-9]+)', handlers.CommentDeleteHandler),
    ('/comments/([0-9]+)', handlers.CommentHandler),
    ('/upvote/([0-9]+)', handlers.UpvoteHandler)
], debug=False)
