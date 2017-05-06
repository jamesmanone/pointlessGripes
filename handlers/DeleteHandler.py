import models
from proto import Handler


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

        @self.logged_in
        def delete_post(post):
            if not self.valid_post(post):
                return
            elif not self.owns_post(post):
                return
            else:
                post.delete()
        delete_post(post)
