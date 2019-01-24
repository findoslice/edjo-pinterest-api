import json
from redis import Redis
from configparser import ConfigParser
from dbhelper import DBHelper
from random import randint
from time import time, strftime, gmtime

from flask_api import FlaskAPI, status, exceptions
from flask import request
from flask.json import jsonify

api = FlaskAPI(__name__)

config = ConfigParser()
config.read('config.ini')

red2 = Redis(db=int(config['redis']['pagesdb']))
red = Redis(db=int(config['redis']['imagesdb']))

es = DBHelper()

@api.route('/search')
def test():

    data = dict(request.data)
    pagesize = 25
    try:
        pagesize = int(data['pagesize'])
    except KeyError:
        pass

    try:
        page = es.searchDB(data['colours'], pagesize=pagesize)
    except:
        return '', status.HTTP_204_NO_CONTENT

    if len(page) == 0:
        return '', status.HTTP_204_NO_CONTENT

    pagekey = str(pagesize) + 'b' + str(randint(0,10000000000))
    red2.set(pagekey, 0)
    if "expire" not in data.keys():
        #expire after 24 hours
        expire = 86400
    
    elif int(data["expire"]) < int(config['api']['maxexpire']):
        expire = int(data["expire"])
    else:
        expire = int(config['api']['maxexpire'])

    red2.expire(pagekey, expire)

    return (jsonify({"next" : pagekey,
                     "nextendpoint": "/next",
                     "expires" : strftime('%Y-%m-%d %H:%M:%S', gmtime(time() + expire)),
                     "expires-epochtime" : int(time() + expire),
                     "images" : page}))


api.run()

"""class GetImages(object):

    def __init__(self):
        
        self.config = ConfigParser()
        self.config.read('config.ini')

        self.red = Redis(db=int(self.config['redis']['imagesdb']))
        self.red2 = Redis(db=int(self.config['redis']['pagesdb']))

        self.es = DBHelper()

    def on_get(self, req, resp):

        data = req.media.get('colours')
        if len(data) == 0:
            resp.body = {"yeet" : "yote"}
            return
        try:
            pagesize = int(req.media.get('pagesize'))
            page = self.es.searchDB(data, pagesize = pagesize)
        except:
            pagesize = 25
            page = self.es.searchDB(data)

        if len(page) == 0:
            resp.status = falcon.HTTP_404
            return

        pagekey = str(pagesize) + 'b' + str(randint(0,10000000000))

        self.red2.add(pagekey, 1)

        resp.body = {
            "next" : pagekey,
            "next-endpoint" : "/next",
            "images" : page
        }
        resp.status = falcon.HTTP_200"""


