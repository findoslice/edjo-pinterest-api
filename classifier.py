from image_parser import get_colours
from elasticsearch import Elasticsearch
from redis import Redis
from configparser import ConfigParser
from hashlib import sha1
from time import sleep

class Classifier(object):

    def __init__(self):

        self.redis = Redis()
        self.es = Elasticsearch()

        self.config = ConfigParser()
        self.config.read('config.ini')

    def run(self):

        while self.redis.scard(self.config['redis']['images-key']) != 0:
            image = self.redis.spop(self.config['redis']['images-key']).decode('utf-8')
            try:
                colours = [colour[1] for colour in get_colours(image)]
            except:
                continue

            imagebody = {
                "url" : image,
                "colours" : colours
            }
            try:
                resp = self.es.index(index="images", doc_type="tagged", body = imagebody, id = (int(sha1(image.encode()).hexdigest(), 16)%10**10))
                print(resp)
            except:
                continue

        while self.redis.scard(self.config['redis']['images-key']) == 0:
            sleep(1)
        
        self.run()

