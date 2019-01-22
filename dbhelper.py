from redis import Redis
from configparser import ConfigParser

class DBHelper(object):

    def __init__():

        self.config = ConfigParser()
        self.config.read('config.ini')

        self.db = Redis(db = int(self.config["redis"]["imagesdb"]))
        self.images = [url.decode('utf-8') for url in self.db.scan("*")]

    def searchdb(*colours):

        colours = [colour.encode() for colour in colours]
        
        correctimages = []

        for image in self.images:

            imagecolours = self.db.smembers("image")

            for colour in colours:
                if colour not in imagecolours:
                    break
            correctimages.append(image)

            
        