import models
import utls
from proto import Handler


class SignupHandler(Handler):  # For /signup
    def get(self):
        '''Sends a signup form. If user is already logged in it redirects to /
        '''
        if not self.user:
            self.render('signup.html')
        else:
            self.redirect('/')

    def post(self):
        '''Takes the signup form data, verifies required fields a populated,
        checks for duplicate username or passwords or usernames too short, and
        if no errors created new User in db and logs the user in
        '''
        username = self.request.get('username')
        password = self.request.get('password')
        passcheck = self.request.get('passcheck')
        email = self.request.get('email')

        in_use = models.User.by_name(username)

        if in_use:
            self.render('signup.html', username=username, email=email,
                        error='Username taken')
        elif password != passcheck:
            self.render('signup.html', username=username, email=email,
                        error='Passwords do not match')
        elif len(password) < 6 or len(username) < 6:
            self.render('signup.html', username=username, email=email,
                        error='Username and password must be a minimum \
                        of 6 characters')
        else:
            password_hash = utls.hashword_converter(username, password)
            newuser = models.User(username=username,
                                  password_hash=password_hash,
                                  email=email, upvotes=0)
            newuser.put()
            self.set_cookie(str(newuser.key().id()))

            self.redirect('/welcome')
