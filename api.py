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
        page = es.searchDB(data['colours'], pagesize=pagesize, cursor = 0)
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

    return (jsonify({"method" : "/search",
                     "next" : pagekey,
                     "nextendpoint": "/next",
                     "expiretime" : expire,
                     "expires" : strftime('%Y-%m-%d %H:%M:%S', gmtime(time() + expire)),
                     "expires-epochtime" : int(time() + expire),
                     "colours" : data["colours"],
                     "pagesize" : pagesize,
                     "images" : page})), status.HTTP_200_OK

@api.route('/count')
def count():

    data = dict(request.data)

    try:
        colours = data['colours']
    except:
        return '', status.HTTP_400_BAD_REQUEST
    
    count = es.countDB(colours)

    return (jsonify({"method" : "/count",
                     "colours" : data['colours'],
                     "result" : count})), status.HTTP_200_OK

@api.route('/count/all')
def count_all():

    return (jsonify({"method" : "/count/all",
                     "result" : es.count_all()})), status.HTTP_200_OK





if __name__ == "__main__":
    api.run()


