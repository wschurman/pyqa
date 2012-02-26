# Requires: mechanize, beautifulsoup, lxml

import sys, time, os
from threading import Thread
from mechanize import Browser
from bs4 import BeautifulSoup

class Scraper(Thread):
	
	def __init__(self, url):
		self.url = url
		Thread.__init__(self)
		
	def run(self):
		br = Browser()
		br.open(self.url)
		self.links = br.links()
		self.html = br.response.read()
		
	def get_links(self):
		return self.links()
		
	def process_html(self):
		soup = BeautifulSoup(self.html)
		content = soup.body
		return body