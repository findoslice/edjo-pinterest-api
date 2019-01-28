from image_parser import get_colours
from elasticsearch import Elasticsearch
from redis import Redis
from configparser import ConfigParser
from hashlib import sha1
from time import sleep
from threading import Thread

class Classifier(Thread):

    def __init__(self, name = "classifier"):

        Thread.__init__(self, name = name)
        self.name = name

        self.es = Elasticsearch()

        self.config = ConfigParser()
        self.config.read('config.ini')

        self.redis = Redis(db = int(self.config['redis']['imagesdb']))

        self.is_stopped = False
        self.is_idle = False

    def stop(self):
        self.is_stopped = True
        #hread.join(self)
        #Thread._stop(self)

    def isIdle(self):
        return self.is_idle

    def run(self):

        try:
            self.is_idle = False
            while self.redis.scard(self.config['redis']['images-key']) != 0:
                if not self.is_stopped:
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
                        #print(resp)
                    except:
                        continue
                else:
                    return
            self.is_idle = True
            while self.redis.scard(self.config['redis']['images-key']) == 0:
                if not self.is_stopped:
                    sleep(1)
                else:
                    return
            
            self.run()

        

        except KeyboardInterrupt:

            print("\nbye bye for now\n")


if __name__ == "__main__":
    classifier = Classifier()
    classifier.run()


