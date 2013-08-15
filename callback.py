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

jinja_env = jinja2.Environment(autoescape=True, 
                                       loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))


class CallBackPage(webapp2.RequestHandler):
    
    def get(self):
        token_key = self.request.get('oauth_token')
        token_secret = self.request.get('oauth_secret')
        sess = dropbox.session.DropboxSession(data.app_key,data.app_secret)
        sess.set_request_token(token_key, token_secret)
        sess.obtain_access_token()
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