from google.appengine.ext import db
import User


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    user = db.ReferenceProperty(User.User, collection_name='posts')

    @property
    def upvote(self):
        return self.upvotes.count()
