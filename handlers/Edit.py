import models
import utls
from proto import Handler


class EditHandler(Handler):  # for /editpost

    def get(self, post_id):
        '''Sends a form to allow user to edit a post
        '''
        post = models.Post.get_by_id(int(post_id))

        @self.logged_in
        def display_editor(post):
            if not post:
                self.error(404)
            elif not self.owns_post(post):
                obj = {
                       'success': False,
                       'message': 'You can only modify your own post'
                }
                self.json(obj)
            else:
                print 'thundercats are goooooo!'
                self.render('editpost.html', subject=post.subject,
                            content=post.content)
        display_editor(post)

    def post(self, post_id):
        '''Takes data from edit form. Verifies user owns the post, and if so
        updates post in db
        '''
        post = models.Post.get_by_id(int(post_id))
        subject = self.request.get('subject')
        content = self.request.get('content')

        @self.logged_in
        def edit(subject, content, post):
            if not self.valid_post:
                return
            elif not self.owns_post(post):
                return
            elif not subject or not content:
                obj = {
                       'success': False,
                       'message': 'We need a subject and some content'
                }
            else:
                post.subject = subject
                post.content = utls.content_escape(content)
                post.put()
                obj = {
                       'success': True,
                       'response': self.render_str('onepost.html', post=post,
                                                   user=self.user)
                }
            self.json(obj)

        edit(subject, content, post)
