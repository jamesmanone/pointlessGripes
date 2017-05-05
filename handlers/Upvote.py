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
        if self.user:
            upvote = post.upvotes.filter('user =', self.user).get()
            if post.user == self.user:
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
                obj = {
                        'success': True,
                        'message': ' ' + str(post.upvote)
                        }
                self.json(obj)
        else:
            self.error(401)
