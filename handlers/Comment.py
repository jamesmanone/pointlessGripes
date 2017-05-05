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
