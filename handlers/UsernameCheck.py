import models
from proto import Handler


class UsernameCheck(Handler):
    '''This is an AJAX handler for on the fly username availability checking.
       linked to signup.js
    '''
    def post(self):
        username = self.request.get('username')
        in_use = models.User.by_name(username)
        if in_use:
            obj = {'taken': True}
        else:
            obj = {'taken': False}
        self.json(obj)
