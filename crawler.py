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
    # instantiate new threads as 50:50 balance of scraper and classifier
    if i%2 == 0:
        threads.append(PinterestScraper(name = "scraper"))
        threadnames.append("scraper")
    else:
        threads.append(Classifier(name = "classifier"))
        threadnames.append("classifier")

for thread in threads:

    thread.start()

def count_scrapers():

    return len([thread for thread in threads if thread.name == "scraper"])

def count_classifiers():

    return len([thread for thread in threads if thread.name == "classifier"])



try:
    while True:
        # remove a scraper and add a classifier if too many unclassified images
        # ensure at least some scrapers remain
        if red.scard(config['redis']['images-key']) > 30 and count_scrapers()/int(config['crawler']['maxthreads']) > 0.2:
            for i in range(len(threads)):
                if threads[i].name == "scraper":
                    threads[i].stop()
                    threads[i] = Classifier(name = "classifier")
                    threadnames[i] = "classifier"
                    threads[i].start()
                    break
                
        for i in range(len(threads)):
            # check if classifiers are idle and if so replace one with a scraper
            if threads[i].name == 'classifier' and count_classifiers()/int(config['crawler']['maxthreads']) > 0.2:
                if threads[i].isIdle() or red.scard(config['redis']['images-key']) < 10:
                    threads[i].stop()
                    threads[i] = PinterestScraper(name = "scraper")
                    threadnames[i] == "scraper"
                    threads[i].start()
                    break

except KeyboardInterrupt:
    for thread in threads:
        thread.stop()
