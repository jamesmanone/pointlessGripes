from google.appengine.ext import db
import Post
import User


class Upvote(db.Model):
    '''This is a log of all upvotes. used to check if
    someone has already upvoted a post
    '''
    post = db.ReferenceProperty(Post.Post, collection_name='upvotes')
    user = db.ReferenceProperty(User.User, collection_name='upvotes_out')
