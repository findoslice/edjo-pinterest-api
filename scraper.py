from bs4 import BeautifulSoup
from redis import Redis
from image_parser import get_colours
from configparser import ConfigParser
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from threading import Thread

from pprint import pprint

from signal import SIGKILL

from requests import get
from time import time
from random import randint
import os,re
import asyncio


class PinterestScraper(Thread):

    def __init__(self, name = "scraper"):
        
        # call super constructor
        Thread.__init__(self, name = name)

        self.config = ConfigParser()
        self.config.read('config.ini')

        self.options = webdriver.chrome.options.Options()

        # options to speed up chrome and ensure it is headless
        self.options.add_argument("--headless")
        self.options.add_argument("--test-type")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.binary_location = str(self.config['chrome']['binary'])
        self.browser = self.new_browser()

        self.db = Redis(db = int(self.config['redis']['searchdb']))
        self.db2 = Redis(db = int(self.config['redis']['imagesdb']))

        self.initial_time = time()
        self.last_time = time()
        self.search_count = 1
        self.sum_search_times = 0

        self.is_stopped = False
        self.name = name

    def stop(self):
        self.is_stopped = True

    def run(self):
        self.search_pinterest("home improvement")

    def new_browser(self):
        return webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), chrome_options=self.options)


    def search_pinterest(self, term):
        wait = WebDriverWait(self.browser,10)
        try:
            self.browser.get("https://www.pinterest.co.uk/search/pins/?q=" + term.lower())
            # wait until images have rendered
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "img")))
            #wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "tBJ dyH iFc SMy MF7 erh tg7 IZT mWe")))

            
            

            soup = BeautifulSoup(self.browser.page_source, str(self.config['soup']['parser']))


            images = soup.find_all("img")

            for image in set([imagetag["src"] for imagetag in images]):
                try:
                    #save images in untagged images set
                    self.db2.sadd(self.config['redis']['images-key'], image)
                except:
                    continue

            # find all pinterest recommended search terms
            # this class name is changed regularly so please let me know if it breaks!
            search_terms = soup.find_all("div", class_ = "tBJ dyH iFc SMy yTZ erh tg7 IZT mWe")
            if len(search_terms) != 0:
                # add search terms to set
                self.db.sadd(str(self.config["redis"]["searchterms-key"]), *set([str(t.get_text()) for t in search_terms]))

            self.sum_search_times += time() - self.last_time

            """print("Search term: {}\nsearch carried out in: {} seconds \ntotal time elapsed: {} seconds\nAverage search time: {}\nTime per Image: {}\nUnused search terms: {}\nUsed search terms: {}\nImages collected: {}\n".format(term, 
                                                                                                                                                                                                                                    time()-self.last_time, 
                                                                                                                                                                                                                                    time()-self.initial_time,
                                                                                                                                                                                                                                    self.sum_search_times/self.search_count,
                                                                                                                                                                                                                                    1/(len(images)/(time()-self.last_time)),
                                                                                                                                                                                                                                    self.db.scard(self.config['redis']['searchterms-key']), 
                                                                                                                                                                                                                                    self.search_count, 
                                                                                                                                                                                                                                    self.db2.scard(self.config['redis']['images-key'])))
            """
            self.search_count += 1
        
        except TimeoutException:
            # sometimes browser times out when loading
            # quit browser and start a new instance if this happens
            self.browser.close()
            # ensure process stops
            self.browser.service.process.send_signal(SIGKILL)
            self.browser.quit()
            #os.system("killall chrome")
            self.browser = self.new_browser()
            print("failed search")

        # choose new search term at random
        term = self.db.spop(str(self.config["redis"]["searchterms-key"])).decode('utf-8')
        self.last_time = time()
        # check if stopped (for purpose of threading)
        if not self.is_stopped:
            self.search_pinterest(term)
        else:
            # same as disposing on timeout error
            self.browser.close()
            self.browser.service.process.send_signal(SIGKILL)
            self.browser.quit()
            return

if __name__ == "__main__":
    pc = PinterestScraper()
    #time1 = time()
    pc.search_pinterest("home improvement")
    #print(time() - time1)
    #pc.browser.close()
    #get_pinterest_image("https://findoslice.com")
