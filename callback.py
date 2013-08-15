'''
Created on Aug 13, 2013

@author: mingxiao10016
'''
import webapp2
import jinja2
import os
import dropbox
import time
import data
import logging
from userToken import UserToken
from google.appengine.ext import db

jinja_env = jinja2.Environment(autoescape=True, 
                                       loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))


class CallBackPage(webapp2.RequestHandler):
    
    def get(self):
        user=self.request.get('user')
        token_key = self.request.get('oauth_token') #request token key
        token_secret = self.request.get('oauth_secret')
        if user and not token_key and not token_secret:
            #this means our user should already be in our DB
            userToken = db.GqlQuery("SELECT * FROM UserToken WHERE username = :1",user).get()
            access_key = userToken.user_key
            access_secret = userToken.user_secret
            self.response.out.write("user already in our database")
        else:
            sess = dropbox.session.DropboxSession(data.app_key,data.app_secret)
            sess.set_request_token(token_key, token_secret)
            access_token = sess.obtain_access_token()
            self.insertNewUser(user,access_token)
            client = dropbox.client.DropboxClient(sess)
            client_data = client.metadata('/')
            files = client_data['contents'] #files is a list of dictionaries
            #get the ten most recently modified files
            filesOnly = self.getFilesOnly(files)
            recentlyModifiedFiles = self.mostRecentlyModified(filesOnly,10)
            d = {'filesToList':recentlyModifiedFiles}
            template = jinja_env.get_template('callback.html')
            logging.info(token_key +" "+token_secret)
            self.response.out.write(template.render(**d))
            
    def insertNewUser(self,user, access_token):
        """
        Inserts a new record into our UserToken table
        """
        newUser = UserToken(username=user, user_key = access_token.key, user_secret = access_token.secret)
        newUser.put()
        
    def getFilesOnly(self,files):
        """
        Given a list of files in dropbox dictionary format, return those files
        where is_dir == False
        
        Returns a list of dictionaries
        """
        filesOnly = []
        for f in files:
            if not f['is_dir']:
                filesOnly.append(f)
        return filesOnly
    
    def mostRecentlyModified(self,files,n):
        """
        Returns the n most recently modified files.
        Returns a list.
        """
        mtime = lambda f: time.strptime(f['modified'], "%a, %d %b %Y %H:%M:%S +0000") 
        filesSorted = sorted(files,key=mtime,reverse=True) #get descending order
        if len(filesSorted)<= n:
            return filesSorted
        else:
            return filesSorted[:n]
        
    def post(self):
#        upload files
        token_key = self.request.get('oauth_token')
        token_secret = self.request.get('oauth_secret')
        sess = dropbox.session.DropboxSession(data.app_key,data.app_secret)

        sess.set_request_token(token_key, token_secret)
        sess.obtain_access_token()
        client = dropbox.client.DropboxClient(sess)
#        f = open('main.py','r')
#        response = client.put_file('/main.py',f)
#        self.response.out.write(response)
        
        

app = webapp2.WSGIApplication([('/callback', CallBackPage),], debug=True)