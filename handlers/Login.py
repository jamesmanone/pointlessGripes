
import models
import utls
from proto import Handler


class LoginHandler(Handler):  # For /login
    def get(self):
        '''sends login page if user is not logged in; else, redirects to /
        '''
        if self.user:
            self.redirect('/')
        else:
            self.render('login.html')

    def post(self):
        '''Validates username and password. If valid, sets a cookie and
        redirects to welcome page
        '''
        name = self.request.get('username')
        password = self.request.get('password')

        if name and password:
            user = models.User.by_name(name)
            salt = user.password_hash.split('|')[1]
        else:
            obj = {'success': False}
            self.json(obj)

        if user and user.password_hash == utls.hashword_converter(name,
                                                                  password,
                                                                  salt):
            self.set_cookie(str(user.key().id()))
            obj = {'success': True}
            self.json(obj)
        else:
            obj = {'success': False}
