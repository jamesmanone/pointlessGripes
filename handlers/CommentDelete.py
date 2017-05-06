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

        @self.logged_in
        def delete_comment(comment):
            if not self.valid_comment(comment):
                return
            elif not self.owns_comment(comment):
                return
            else:
                comment.delete()
                obj = {
                        'success': True
                }
                self.json(obj)

        delete_comment(comment)
