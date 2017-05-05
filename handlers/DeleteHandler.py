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
        if not self.user:
            self.redirect('/login')
        elif self.user != post.user:
            self.render('permalink.html',
                        error='You cannot delete someone elses post')
        else:
            post.delete()
