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
red3 = Redis(db=int(config['redis']['coloursdb']))

es = DBHelper()

@api.route('/search', methods = ['GET', 'POST'])
def search():

    data = dict(request.data)
    pagesize = 25
    try:
        print(data['pagesize'])
        pagesize = int(data['pagesize'][0])
    except KeyError:
        pass

    try:
        page = es.searchDB(data['colours'], pagesize=pagesize, cursor = 0)
    except:
        # if search is malformed return no content
        return '', status.HTTP_204_NO_CONTENT

    if len(page) == 0:
        # if nothign is found return no content
        return '', status.HTTP_204_NO_CONTENT

    # generate next token and add to redis databases
    pagekey = str(pagesize) + 'b' + str(randint(0,10000000000))
    red2.set(pagekey, 0)
    red3.sadd(pagekey, *set(data['colours']))

    if "expire" not in data.keys():
        #expire after 24 hours
        expire = 86400
    elif int(data["expire"]) < int(config['api']['maxexpire']):
        expire = int(data["expire"])
    else:
        #set expiry time to maximum expiry time
        expire = int(config['api']['maxexpire'])

    red2.expire(pagekey, expire*1000)
    red3.expire(pagekey, expire*1000)

    return (jsonify({"method" : "/search",
                     "next" : pagekey,
                     "nextendpoint": "/next",
                     "expiretime" : expire,
                     "expires" : strftime('%Y-%m-%d %H:%M:%S', gmtime(time() + expire)),
                     "expires-epochtime" : int(time() + expire),
                     "colours" : data["colours"],
                     "pagesize" : pagesize,
                     "images" : page})), status.HTTP_200_OK

@api.route('/next/<token>', methods = ['GET', 'POST'])
def next(token):

    #find pagesize from token
    pagesize = int(token.split('b')[0])

    cursor = red2.get(token)
    if info is None:
        # if token has expired return no content
        return '', status.HTTP_204_NO_CONTENT
    expire = red2.pttl(token)
    # convert stored token to int
    cursor = int(info.decode('utf-8'))
    # convert colours from byte string
    colours = [colour.decode('utf-8') for colour in red3.smembers(token)]
    # increment cursor
    red2.incr(token)

    # get next page from db
    page = es.searchDB(colours, pagesize = pagesize, cursor = cursor)
    if len(page) == 0:
        # if no more matching colours remain from the search query, delete the token and return 204 no content
        red2.delete(token)
        return '', status.HTTP_204_NO_CONTENT


    return (jsonify({"method" : "/next/" + token,
                     "next" : token,
                     "nextendpoint": "/next",
                     "expiretime" : expire,
                     "expires" : strftime('%Y-%m-%d %H:%M:%S', gmtime(time() + expire/1000)),
                     "expires-epochtime" : int(time() + expire),
                     "colours" : colours,
                     "pagesize" : pagesize,
                     "images" : page})), status.HTTP_200_OK

@api.route('/next/delete/<token>', methods = ['GET', 'POST', 'DELETE'])
def delete_next(token):

    # just deletes the token
    red2.delete(token)
    red3.delete(token)

    return '', status.HTTP_200_OK

@api.route('/are/you/a/tea/pot', methods = ['GET', 'POST'])
def am_I_a_tea_pot():

    #confirms whether or not server is a teapot
    return (jsonify({'teapot':{'status':'true'}})), 418


@api.route('/count', methods = ['GET', 'POST'])
def count():

    data = dict(request.data)

    try:
        colours = data['colours']
    except:
        # if colours are not specified return bad request
        return '', status.HTTP_400_BAD_REQUEST
    
    count = es.countDB(colours)

    return (jsonify({"method" : "/count",
                     "colours" : data['colours'],
                     "count" : count})), status.HTTP_200_OK

@api.route('/count/all', methods = ['GET', 'POST'])
def count_all():

    return (jsonify({"method" : "/count/all",
                     "count" : es.count_all()})), status.HTTP_200_OK





if __name__ == "__main__":
    api.run()


