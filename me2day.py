#
# -*- coding: utf-8 -*-
# 
# Author: Jang-Ho Hwang <rath@xrath.com>
# Version: 1.0, since 2009/09/13
#
import httplib, urllib
import base64, hashlib, random
from datetime import datetime

import json

class Post:
    def __init__(self):
        self.id = None
        self.permalink = None
        self.author = None
        self.body = None
        self.body_as_text = None
        self.metoo_count = 0
        self.comment_count = 0
        self.tags = []
        self.date = None
    def __str__(self):
        return "<me2day.Post#%s, %s>" % (self.id, self.author.id)

class Person:
    def __init__(self):
        self.id = None
        self.nickname = None
        self.me2day_home = None
        self.openid = None 
        self.description = None
        self.face = None
        self.homepage = None
        self.friend_count = 0
        self.updated = None
    def __str__(self):
        return "<me2day.Person#%s, %s>" % (self.id, self.nickname)

class Comment:
    def __init__(self):
        self.id = None
        self.author = None
        self.body = None
        #self.body_as_text = None
        self.date = None
    def __str__(self):
        return "<me2day.Comment#%s, %s at %s>" % (self.id, self.author.id, self.date)

"""
    me2DAY API wrapper.

    TODO: The current implementation doesn't support TimeZone on each Post, Comment instance.
    TODO: To handle exceptional i/o error.
"""
class me2API:
    HOST = 'me2day.net'

    def __init__(self, username=None, userkey=None, app_key=None):
        self.username = username
        self.headers = {}
        if app_key:
            self.headers['me2_application_key'] = app_key
        if username and userkey:
            self.headers['Authorization'] = "Basic %s" % self._create_auth(username,userkey)

    def _create_auth(self, id, pw):
        nonce = hashlib.md5((random.random()*(10**10)).__str__()).hexdigest()[:8]
        return base64.b64encode("%s:%s%s" % (id, nonce, hashlib.md5(nonce+pw).hexdigest()))

    def _get(self, uri, processor=None, params={}):
        con = httplib.HTTPConnection(self.HOST, 80, timeout=10)
        ret = None
        try:
            con.request("GET", uri, urllib.urlencode(params), self.headers)
            res = con.getresponse()
            if res.status/100==4:
                raise Error("%d %s" % (res.status, res.reason))
            data = res.read()
            if processor:
                ret = processor(json.loads(data))
        finally:
            con.close()
        return ret

    def _post(self, uri, processor=None, params={}):
        con = httplib.HTTPConnection(self.HOST, 80, timeout=10)
        head = self.headers
        head['Content-Type'] = 'application/x-www-form-urlencoded'

        ret = None
        try:
            con.request("POST", uri, urllib.urlencode(params), head)
            res = con.getresponse()
            if res.status/100==4:
                raise Error("%d %s" % (res.status, res.reason))
            data = res.read()
            if processor:
                ret = processor(json.loads(data))
        finally:
            con.close()
        return ret
        
    def _process_get_posts(self, json_data):
        ret = []
        for post in json_data:
            p = Post()
            p.id = post['post_id']
            p.permalink = post['permalink']
            p.body = post['body']
            p.body_as_text = post['textBody']
            p.metoo_count = post['metooCount']
            p.comment_count = post['commentsCount']
            p.date = datetime.strptime(post['pubDate'][:-5], "%Y-%m-%dT%H:%M:%S")
            p.tags = filter(lambda x: len(x) > 0, post['tagText'].split(' '))
            
            author = Person()
            author.id = post['author']['id']
            author.nickname = post['author']['nickname']
            author.me2day_home = post['author']['me2dayHome']
            author.face = post['author']['face']
            p.author = author
            ret.append(p)
        return ret

    def _process_get_comments(self, json_data):
        ret = []
        for cmt in json_data['comments']:
            c = Comment()
            c.id = cmt['commentId']
            c.body = cmt['body']
            c.date = datetime.strptime(cmt['pubDate'][:-5], "%Y-%m-%dT%H:%M:%S")

            author = Person()
            author.id = cmt['author']['id']
            author.nickname = cmt['author']['nickname']
            author.face = cmt['author']['face']
            author.me2day_home = cmt['author']['me2dayHome']
            c.author = author
            ret.append(c)
        return ret

    def _process_get_friends(self, json_data):
        ret = []
        for f in json_data['friends']:
            p = Person()    
            p.id = f['id']
            p.nickname = f['nickname']
            p.face = f['face']
            p.me2dayHome = f['me2dayHome']
            p.friendsCount = f['friendsCount']
            p.updated = f['updated']
            ret.append(p)
        return ret

    def _process_get_metoos(self, json_data):
        ret = []
        for m in json_data['metoos']:
            p = Person()
            p.id = m['author']['id']
            p.nickname = m['author']['nickname']
            p.face = m['author']['face']
            p.me2day_home = m['author']['me2dayHome']

            ret.append( (p, m['pubDate']) )
        return ret

    def _process_metoo(self, json_data):
        return (json_data['code'], json_data['message'], json_data['description'])

    def get_posts(self, params={}, username=None):
        if not username:
            username = self.username
        querystring = urllib.urlencode(params)
        return self._get("/api/get_posts/%s.json?%s" % (username, querystring), 
            self._process_get_posts)

    def get_comments(self, params={}, username=None):
        if not username:
            username = self.username
        querystring = urllib.urlencode(params)
        return self._get("/api/get_comments/%s.json?%s" % (username, querystring),
            self._process_get_comments)

    def create_comment(self, params={}, username=None):
        """
        Parameters 'post_id' and 'body' must be set before invoke this method. 
        """
        if not username and not self.username:
            raise Error('username and userkey must be set')
        return self._post("/api/create_comment.json", None, params)

    def create_post(self, params={}, username=None):
        """
        Supported parameters:
        * post[body] - a body of the post.
        * post[tags] - tags separated by space(0x20).
        * post[icon] - icon index between 1 and 12.
        * close_comment - set true if you don't want to be welcome any comments.
        * receive_sms - set true if you want to receive sms when other users add a comment.
        """
        if not username and not self.username:
            raise Error('username and userkey must be set')
        return self._post("/api/create_post.json", None, params)

    def get_friends(self, params={}, username=None):
        """
        Supported parameters:
        * scope=all - All of friends
        * scope=close - Friends who have close relationship.
        * scope=supporter - Supporters up to 30. (auth required)
        * scope=sms - Interesting friends up to 30. (auth required)
        * scope=family - Friends who invite me, who was invited by me.
        * scope=mytag[_tagname_] - (auth required)
        * scope=group[_name_] - (auth required)
        """
        if not username:
            username = self.username
        querystring = urllib.urlencode(params)
        return self._get("/api/get_friends/%s.json?%s" % (username, querystring), 
            self._process_get_friends)

    def get_metoos(self, params={}):
        """
        Get a list of persons who clicked metoo on a specific post.
        * post_id: id of the post.
        """
        querystring = urllib.urlencode(params)
        return self._get("/api/get_metoos.json?%s" % querystring, self._process_get_metoos)

    def metoo(self, params={}, username=None):
        """
        Submit a metoo to a specific post.
        * post_id: id of the post.
        """
        if not username and not self.username:
            raise Error('username and userkey must be set')
        querystring = urllib.urlencode(params)
        return self._get("/api/metoo.json?%s" % querystring, self._process_metoo)

    def noop(self):
        """
        No operation. but test your authentication.
        """
        return self._get("/api/noop.json")

class Error(Exception):
    pass

