from redis import Redis
from configparser import ConfigParser

class DBHelper(object):

    def __init__():

        self.config = ConfigParser()
        self.config.read('config.ini')

        self.db = Redis(db = int(self.config["redis"]["imagesdb"]))

    def searchdb(*colours):
        
        links = set(self.db.smembers(colours[0]))

        for colour in colours[1:]:
            links -= set(self.db.smembers(colour))

        return [link.decode('utf-8') for link in links]

            
        