import models
from proto import Handler


class UsernameCheck(Handler):
    def post(self):
        username = self.request.get('username')
        in_use = models.User.by_name(username)
        if in_use:
            obj = {'taken': True}
        else:
            obj = {'taken': False}
        print obj
        self.json(obj)
