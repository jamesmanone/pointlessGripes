import models
from proto import Handler


class UpvoteHandler(Handler):
    # This is an AJAX handler. Do not navigate here
    def post(self, post_id):
        '''If user is logged in and hasn't already upvoted this post this will
        add an upvote to the upvote db and increment the post upvote count by
        1. If successful, success: True, and new upvote count is sent in JSON.
        If user is no logged in or has already upvoted this post success: False
        and error message is sent in JSON
        '''
        post = models.Post.get_by_id(int(post_id))

        @self.logged_in
        def new_upvote(post, post_id):
            if not self.valid_post(post):
                return
            upvote = post.upvotes.filter('user =', self.user).get()
            if post.user.key() == self.user.key():
                self.response.headers['Content-Type'] = 'application/json'
                obj = {
                        'success': False,
                        'message': 'You cant upvote your own post!'
                        }
                self.json(obj)
            elif upvote:
                self.response.headers['Content-Type'] = 'application/json'
                obj = {
                        'success': False,
                        'message': 'You can\'t upvote again'
                        }
                self.json(obj)
            else:
                upvote = models.Upvote(user=self.user, post=post)
                upvote.put()
                post = models.Post.get_by_id(int(post_id))
                obj = {
                        'success': True,
                        'message': ' ' + str(post.upvote + 1)
                        }
                self.json(obj)
        new_upvote(post, post_id)
