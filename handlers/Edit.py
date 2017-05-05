import main
import models
from proto import Handler


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
            post.content = main.content_escape(content)
            post.put()
            self.redirect('/permalink/{0}'.format(post_id))
