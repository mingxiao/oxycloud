import webapp2
import jinja2
import os
import dropbox
import data
import logging
from userToken import UserToken
from google.appengine.ext import db

jinja_env = jinja2.Environment(autoescape=True, 
                                       loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('index.html')
        self.response.out.write(template.render())
#        sess = dropbox.session.DropboxSession(data.app_key,data.app_secret)
#        request_token = sess.obtain_request_token()
#        logging.info(request_token.key+','+request_token.secret)
#        self.response.out.write(request_token.key+','+request_token.secret)
#        callback_url = self.request.url + 'callback?oauth_secret={}'.format(request_token.secret)
#        auth_url = sess.build_authorize_url(request_token, callback_url)
#        self.redirect(auth_url)
        
    def post(self):
        user = self.request.get('user')
        userToken = db.GqlQuery("SELECT * FROM UserToken WHERE user_id = :1",user).get()
        if userToken:
            self.response.out.write('user exists')
            pass
        else:
            self.response.out.write('user does not exists')
            pass
        #check if we have that user in our DB
        pass
        

app = webapp2.WSGIApplication([('/', MainPage),], debug=True)