'''
Created on Aug 15, 2013

@author: mingxiao10016
'''
from google.appengine.ext import db

"""
Access token per user
"""
class UserToken(db.Model):
    username= db.StringProperty(required =True)
    user_key = db.StringProperty(required = True)
    user_secret = db.StringProperty(required =True)
    created = db.DateTimeProperty(auto_now_add=True)
    