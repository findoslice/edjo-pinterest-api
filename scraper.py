from bs4 import BeautifulSoup
from selenium import webdriver
from requests import get

def get_pinterest_image(url):
    browser = webdriver.Firefox()
    browser.get(url)
    print(browser.title)
    images = browser.find_element_by_css_selector("_u3 _45 _y8 _4h")
    print(images)
    browser.close()

#get_pinterest_image("https://www.pinterest.co.uk/pin/353321533260110279/")
get_pinterest_image("https://findoslice.com")