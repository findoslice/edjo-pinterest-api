from bs4 import BeautifulSoup
from redis import Redis
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from requests import get
from time import time
from random import randint
import os,re
import asyncio


class PinterestCrawler(object):

    def __init__(self):
        options = webdriver.chrome.options.Options()
        options.add_argument("--headless")
        options.add_argument("--test-type")
        options.add_argument('--ignore-certificate-errors')
        options.binary_location = '/usr/bin/google-chrome'
        self.browser = self.new_browser()

        self.db = Redis()

        self.initial_time = time()
        self.last_time = time()
        self.search_count = 1
        self.sum_search_times = 0

    def new_browser(self):
        options = webdriver.chrome.options.Options()
        options.add_argument("--headless")
        options.add_argument("--test-type")
        options.add_argument('--ignore-certificate-errors')
        options.binary_location = '/usr/bin/google-chrome'
        return webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), chrome_options=options)


    def search_pinterest(self, term):
        wait = WebDriverWait(self.browser,4)
        try:
            self.browser.get("https://www.pinterest.co.uk/search/pins/?q=" + term.lower())
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "img")))
            
            

            soup = BeautifulSoup(self.browser.page_source, 'html.parser')


            images = soup.find_all("img")
            self.db.sadd('untaggedimages', *set([image["src"] for image in images]))


            search_terms = soup.find_all("div", class_ = "_wa _0 _1 _2 _wd _36 _f _b _6")
            if len(search_terms) != 0:
                self.db.sadd('pizza', *set([str(t.get_text()) for t in search_terms]))

            self.sum_search_times += time() - self.last_time

            print("Search term: {}\nsearch carried out in: {} seconds \ntotal time elapsed: {} seconds\nAverage search time: {}\nTime per Image: {}\nUnused search terms: {}\nUsed search terms: {}\nImages collected: {}\n".format(term, 
                                                                                                                                                                                                                                    time()-self.last_time, 
                                                                                                                                                                                                                                    time()-self.initial_time,
                                                                                                                                                                                                                                    self.sum_search_times/self.search_count,
                                                                                                                                                                                                                                    1/(len(images)/(time()-self.last_time)),
                                                                                                                                                                                                                                    self.db.scard('pizza'), 
                                                                                                                                                                                                                                    self.search_count, 
                                                                                                                                                                                                                                    self.db.scard('untaggedimages')))
            self.search_count += 1
        
        except TimeoutException:
            self.browser.quit()
            self.browser = self.new_browser()
            print("failed search")

        term = self.db.spop('pizza').decode('utf-8')
        self.last_time = time()

        self.search_pinterest(term)


pc = PinterestCrawler()
time1 = time()
pc.search_pinterest("home improvement")
print(time() - time1)
pc.browser.close()
#get_pinterest_image("https://findoslice.com")