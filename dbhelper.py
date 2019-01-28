from elasticsearch import Elasticsearch
from configparser import ConfigParser

class DBHelper(object):

    def __init__(self):

        self.config = ConfigParser()
        self.config.read('config.ini')

        self.es = Elasticsearch()

    def searchDB(self, colours, pagesize = 25, cursor = 0):
        # select url where user specified colours present, specify cursor and pagesize
        body = {
                "_source":["url"],
                "from" : cursor, "size" : pagesize,
                "query" : {
                    "bool" : {
                    "must" : [
                    {"match":{
                        "colours":colour
                    }} for colour in colours]
                    }
                }
            }
        # execute search
        res = self.es.search(index="images", doc_type="tagged", body=body)
        # convert result to list of links
        res = [url['_source']['url'] for url in res['hits']['hits']]

        return res

    def countDB(self, colours):
            # same as before except returning a count
            body = {
                "query" : {
                    "bool" : {
                    "must" : [
                    {"match":{
                        "colours":colour
                    }} for colour in colours]
                    }
                }
            }
            # execute search
            res = self.es.count(index="images", doc_type="tagged", body=body)
            # get the count from result
            return int(res['count'])

    def count_all(self):

        return int(self.es.count(index="images", doc_type="tagged")['count'])
        