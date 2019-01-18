from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests import get
import os

def get_pinterest_image(url):
    options = webdriver.chrome.options.Options()
    options.add_argument("--headless")
    options.add_argument("--test-type")
    options.add_argument('--ignore-certificate-errors')
    options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    browser = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), chrome_options=options)
    wait = WebDriverWait(browser, 10)
    browser.get(url)
    #wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "_4f _h _xu _4q")))
    print(browser.page_source)
    #images = browser.find_element_by_css_selector("_u3 _45 _y8 _4h")
    #print(images)
    browser.close()

get_pinterest_image("https://www.pinterest.co.uk/search/pins/?q=yeet")
#get_pinterest_image("https://findoslice.com")