import falcon, json
from redis import Redis
from configparser import ConfigParser
from dbhelper import DBHelper
from random import randint

api = falcon.API()

class GetImages(object):

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
        resp.status = falcon.HTTP_200

api.add_route('/search', GetImages())


