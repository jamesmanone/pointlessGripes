import models
from proto import Handler


class OnepostHandler(Handler):
    def get(self, post_id):
        post = models.Post.get_by_id(int(post_id))
        if not self.valid_post(post):
            return
        elif not self.user:
            self.render('onepost.html', post=post)
        else:
            self.render('onepost.html', post=post, user=self.user)
