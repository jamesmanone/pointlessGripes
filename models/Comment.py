from google.appengine.ext import db
import Post
import User


class Comment(db.Model):
    post = db.ReferenceProperty(Post.Post, collection_name='comments')
    user = db.ReferenceProperty(User.User, collection_name='comments')
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
