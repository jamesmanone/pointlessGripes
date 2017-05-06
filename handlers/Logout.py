
from proto import Handler


class LogoutHandler(Handler):  # For /logout
    def get(self):
        '''Sets cookie to 'user=;' and redirects logged out user to /
        '''
        @self.logged_in
        def logout():
            self.response.headers.add_header("Set-Cookie", 'user=; Path=/')
            self.redirect('/')

        logout()
