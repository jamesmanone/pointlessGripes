import models
from proto import Handler


class UserHandler(Handler):  # For /user/{username}
    '''Retrieves posts by a specified user and displays them
    '''
    def get(self, user_id):
        user = models.User.by_name(user_id)
        if user:
            posts = user.posts.order('-created')
        else:
            self.error(404)
            return
        if posts:
            if self.user:
                self.render('user.html', posts=posts, user=self.user,
                            title=user_id)
            else:
                self.render('user.html', posts=posts, title=user_id)
        else:
            self.error(404)
