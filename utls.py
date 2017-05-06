import secret
import hashlib
import hmac
import random
from string import letters


def make_cookie_hash(user):
    '''Takes user id and returns user id and hashstring for cookie
    '''
    return '{0}|{1}'.format(user, hmac.new(secret.secret, user).hexdigest())


def check_cookie_hash(cookie):
    '''Takes cookie as input, verifies the hash, and returns the user id
    '''
    user = cookie.split('|')[0]
    if cookie == make_cookie_hash(user):
        return user


def make_salt():
    '''Does like morton
    '''
    return ''.join(random.choice(letters) for x in xrange(5))


def hashword_converter(name, password, salt=make_salt()):
    '''converts name + password + ?salt to password hash + salt.
    Gets salt from make_salt() if none provided
    '''
    return '{0}|{1}'.format(
            hashlib.sha256(name + password + salt).hexdigest(), salt)


def password_valid(name, password, password_hash):
    '''Takes username, password, and saved password_hash. Returns true
    if password_hash matches the result of hashing password
    '''
    salt = password_hash.split('|')[1]
    if hashword_converter(name, password, salt) == password_hash:
        return True


def content_escape(content):
    '''Escapes HTML and subsequently unescapes tags that are allowed. also
    converts newlines to <br>
    '''
    content = str(content)
    content = content.replace('&', '&amp;')
    content = content.replace('<', '&lt;')
    content = content.replace('>', '&gt;')
    content = content.replace('"', '&quot;')
    content = content.replace('&lt;b&gt;', '<b>')
    content = content.replace('&lt;/b&gt;', '</b>')
    content = content.replace('&lt;strong&gt;', '<strong>')
    content = content.replace('&lt;/strong&gt;', '</strong>')
    content = content.replace('&lt;em&gt;', '<em>')
    content = content.replace('&lt;/em&gt;', '</em>')
    content = content.replace('&lt;br&gt;', '<br>')
    content = content.replace('&lt;code&gt;', '<code>')
    content = content.replace('&lt;/code&gt;', '</code>')
    content = content.replace('&lt;u&gt;', '<u>')
    content = content.replace('&lt;/u&gt;', '</u>')
    content = content.replace('\n', '<br>')
    content = content.replace('  ', '&nbsp;&nbsp;')
    return content
