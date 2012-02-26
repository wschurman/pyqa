# Requires: celery, mechanize, beautifulsoup, lxml
from celery.task import task
from threading import Thread, Lock
from mechanize import Browser
from bs4 import BeautifulSoup
from Queue import Queue, Empty
#import scraper

num_workers = 4

visited = set()
urls = Queue()

r_lock = Lock()
results = []

class ScrapeData:
	
	def __init__(self, url, depth):
		self.url = url
		self.scraped = False
		self.depth = depth
	
	def __hash__(self):
		return self.url
	
	def scraped(self):
		return self.scraped
	
	def get_url(self):
		return self.url
	
	def set_content(self, c):
		self.content = c
		self.scraped = True
		
	def get_content(self):
		return self.content
	
	def get_depth(self):
		return self.depth


class ScraperWorker(Thread):
	
	def __init__(self, timeout):
		self.scrape_data = None
		self.initial_timeout = timeout
		self.timeout = timeout
		Thread.__init__(self)
		
	def run(self):
		global urls, visited, r_lock
		
		try:
			while True:
				self.scrape_data = urls.get(False, self.timeout)		
				
				try:
					br = Browser()
					br.open(self.scrape_data.get_url())
					assert br.viewing_html()
					
					for link in br.links():
						if link.base_url not in visited:
							urls.put(ScrapeData(link.base_url, self.scrape_data.get_depth() - 1))
							visited.add(link.base_url)
					
					resp = br.response
					print br.title()
					soup = BeautifulSoup(resp.get_data())
					self.scrape_data.set_content(soup.body)
					with r_lock:
						results.append(self.scrape_data)
						self.scrape_data = None
				except Exception as e:
					print e
		except Empty:
			pass
			

@task
def crawl(url, maxdepth):
	global urls, visited
	if maxdepth == 0: return -1
	
	urls.put(ScrapeData(url, maxdepth))
	visited.add(url)
	
	workers = []
	for i in range(0, num_workers):
		r = ScraperWorker(2)
		r.start()
		workers.append(r)
	
	for worker in workers:
		worker.join()
		
if __name__ == '__main__':
	crawl("http://wschurman.com/", 3)