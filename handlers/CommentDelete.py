import models
from proto import Handler


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
