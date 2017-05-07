import models
from proto import Handler


class EditComment(Handler):
    '''Handles sending comment edit form and processing edits. Requires user
    to own the comment they are trying to edit before recieving the edit form
    or posting an update
    '''
    def get(self, comment_id):
        comment = models.Comment.get_by_id(int(comment_id))

        @self.logged_in
        def comment_form(comment):
            if not self.valid_comment(comment):
                return
            elif not self.owns_comment(comment):
                return
            else:
                obj = {
                       'success': True,
                       'response': self.render_str('editcomment.html',
                                                   comment=comment)
                }
            self.json(obj)
        comment_form(comment)

        def post(self, comment_id):
            newcomment = self.request.get('comment')
            cancel = self.request.get('cancel')
            comment = models.Comment.get_by_id(int(comment_id))

            @self.logged_in
            def edit_comment(comment, newcomment):
                if not self.valid_comment(comment):
                    return False
                elif not self.owns_comment(comment):
                    return False
                else:
                    comment.comment = newcomment
                    comment.put()
                    return True

            success = True
            if not cancel:
                success = edit_comment(comment, newcomment)
            if success:
                obj = {
                       'success': True,
                       'response': self.render_str('comment.html',
                                                   comments=comment)
                }
                self.json(obj)
