'''
Created on Aug 15, 2013

@author: mingxiao10016
'''
from google.appengine.ext import db

"""
Access token per user
"""
class UserToken(db.Model):
    user= db.StringProperty(required =True)
    key = db.StringProperty(required = True)
    secret = db.StringProperty(requred =True)
    created = db.DateTimeProperty(auto_now_add=True)
    