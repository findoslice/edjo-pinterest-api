from elasticsearch import Elasticsearch
from configparser import ConfigParser

class DBHelper(object):

    def __init__(self):

        self.config = ConfigParser()
        self.config.read('config.ini')

        self.es = Elasticsearch()

    def searchDB(self, colours, pagesize = 25):

        body = {
                "_source":["url"],
                "from" : 0, "size" : pagesize,
                "query" : {
                    "bool" : {
                    "must" : [
                    {"match":{
                        "colours":colour
                    }} for colour in colours]
                    }
                }
            }

        res = self.es.search(index="images", doc_type="tagged", body=body)

        res = [url['_source']['url'] for url in res['hits']['hits']]

        return res

            
        