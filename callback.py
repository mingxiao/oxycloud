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
        #get the access key and secret
        if user and not token_key and not token_secret:
            #this means our user should already be in our DB
            userToken = db.GqlQuery("SELECT * FROM UserToken WHERE username = :1",user).get()
            access_key = userToken.user_key
            access_secret = userToken.user_secret
            sess = dropbox.session.DropboxSession(data.app_key,data.app_secret)
            sess.set_token(access_key, access_secret)
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
        #for right now just upload a dummy file
        user = self.request.get('user')
        uploadFile = self.request.get('upload')
        self.response.out.write(uploadFile)
        userToken = db.GqlQuery("SELECT * FROM UserToken WHERE username = :1",user).get()
        access_key = userToken.user_key
        access_secret = userToken.user_secret
        sess = dropbox.session.DropboxSession(data.app_key,data.app_secret)
        sess.set_token(access_key, access_secret)
        client = dropbox.client.DropboxClient(sess)
        
        download = self.request.get('do_download')
        upload = self.request.get('do_upload')
        if download:
            f, metadata = client.get_file_and_metadata('/magnum-opus.txt')
            home = os.path.expanduser("~")
            outfile = os.path.join(home,'dropbox_dl.txt')
            out = open(outfile, 'w')
            out.write(f.read())
            out.close()
            print metadata
            self.response.out.write("d/l")
        else:
            self.response.out.write('u/l')

        

app = webapp2.WSGIApplication([('/callback', CallBackPage),], debug=True)