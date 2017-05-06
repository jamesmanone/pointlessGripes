
import utls
import models
from proto import Handler


class NewPostHandler(Handler):  # For /newposts
    def get(self):
        '''Sends new post form if user is logged in, else redirects to /login
        '''
        @self.logged_in
        def new_post():
            self.render('newpost.html', user=self.user)
        new_post()

    def post(self):
        '''Takes data from newpost form. If all fields are populated the
        content field will go through a custom escape function that allows
        some formatting html and replaces new lines with <br>. This data is
        passed to the Post constructer to be added to the db. The user is then
        redirected to the post's permalink
        '''
        subject = self.request.get('subject')
        content = self.request.get('content')

        @self.logged_in
        def make_post(subject, content):
            if not subject or not content:
                obj = {
                       'success': False,
                       'message': 'We need a subject and some content'
                }
            else:
                content = utls.content_escape(content)
                post = models.Post(subject=subject, content=content,
                                   user=self.user)
                post.put()
                obj = {
                       'success': True,
                       'post_id': post.key().id()
                }
            self.json(obj)
        make_post(subject, content)
