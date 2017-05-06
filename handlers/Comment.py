import models
from proto import Handler


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

        comment = self.request.get('comment')
        post = models.Post.get_by_id(int(post_id))

        @self.logged_in
        def post_comment(post, comment):
            if not self.valid_post:
                return
            elif not comment:
                obj = {
                       'success': False,
                       "message": 'You have to type a comment'
                }
            else:
                comment = models.Comment(user=self.user, comment=comment,
                                         post=post)
                comment.put()
                obj = {
                        'success': True,
                        'result': self.render_str('newcommentresponse.html',
                                                  comment=comment,
                                                  user=self.user)
                        }
                self.json(obj)

        post_comment(post, comment)
