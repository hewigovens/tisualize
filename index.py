# conding:utf-8

import web
from fetch import get_hot_list
import logging
from config import CONSUMER_KEY,CONSUMER_SECRET,CALLBACK_URL
from weibopy.auth import OAuthHandler
from weibopy.api import API

logging.basicConfig(level=0,format="%(asctime)s %(levelname)s %(message)s")

urls = ("/",'Home',
        "/callback","CallBack",
        "/analyze","Analyzer")

render = web.template.render('templates/')

app = web.application(urls,globals())


if web.config.get("_session") is None:
    session=web.session.Session(app,web.session.DiskStore("tisualize"))
    web.config._session=session
else:
    session=web.config._session

class Home():
    '''Home Page'''
    def GET(self):
        access_token=session.get('access_token',None)
        if not access_token:
            auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET,web.ctx.get('homedomain')+'/callback')
            auth_url = auth.get_authorization_url()
            session.request_token=auth.request_token
            web.seeother(auth_url)
        else:
            auth =OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.access_token=access_token
            api=API(auth)
            user=api.verify_credentials()
            user_timeline=user.timeline(count=10)

            print "current user is ",user.screen_name
            hot_list=get_hot_list()
            for user_tweet in user_timeline:
                try:
                    hot_list.append(tuple([user_tweet.user.screen_name,
                                            user_tweet.mid,
                                            user_tweet.text,
                                            user_tweet.source,
                                            user_tweet.created_at,
                                            None,
                                            None]))
                except AttributeError:
                    #no retweet_statues
                    continue
            return render.index(user.screen_name,user.id,hot_list)


class Analyzer():
    '''Analyzer'''
    def GET(self):
        indata=web.input()
        query=indata.get('query',None)
        logging.info("access_token is %s" % (session.get('access_token')))
        self.analyze(query)
        return render.tweets(query)


    def analyze(self,query):
        if query=="" or query is None:
            web.seeother("/")
        access_token=session.get('access_token',None)
        auth =OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.access_token=access_token
        api=API(auth)
        repost_timeline=api.repost_timeline(count=10)
        print repost_timeline
        logging.info("analyzing query %s " % (query))


class CallBack():
    def GET(sefl):
        ins=web.input()
        oauth_verifier=ins.get('oauth_verifier',None)
        request_token=session.get('request_token',None)
        auth=OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.request_token=request_token

        access_token=auth.get_access_token(oauth_verifier)
        session.access_token=access_token
        web.seeother("/")

if __name__=="__main__":
    app.run()