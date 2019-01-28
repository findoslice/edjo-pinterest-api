from redis import Redis
from scraper import PinterestScraper
from classifier import Classifier
from configparser import ConfigParser

threads = []
threadnames = []

config = ConfigParser()
config.read('config.ini')

red = Redis(db = 1)

for i in range(int(config['crawler']['maxthreads'])):
    print("skeet")
    if i%2 == 0:
        threads.append(PinterestScraper(name = "scraper"))
        threadnames.append("scraper")
    else:
        threads.append(Classifier(name = "classifier"))
        threadnames.append("classifier")

for thread in threads:

    thread.start()


try:
    while True:

        if red.scard(config['redis']['images-key']) > 50:
            for i in range(len(threads)):
                if threads[i].name == "scraper":
                    threads[i].stop()
                    threads[i] = Classifier(name = "classifier")
                    threadnames[i] = "classifier"
                    threads[i].start()
                    break
                
        for i in range(len(threads)):
            if threads[i].name == 'classifier':
                if threads[i].isIdle():
                    threads[i].stop()
                    threads[i] = PinterestScraper(name = "scraper")
                    threadnames[i] == "scraper"
                    threads[i].start()
                    break

except KeyboardInterrupt:
    for thread in threads:
        thread.stop()
