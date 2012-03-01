# Requires: celery, mechanize, beautifulsoup, lxml
from celery.task import task
from threading import Thread, Lock
from Queue import Queue, Empty
import re
import mechanize
from scraper import ScrapeData

num_workers = 4

visited = set()
urls = Queue()

r_lock = Lock()
results = []
			

class ScraperWorker(Thread):
	
	def __init__(self, timeout):
		self.scrape_data = None
		self.initial_timeout = timeout
		self.timeout = timeout
		Thread.__init__(self)
		
	def run(self):
		global urls, visited, r_lock
		
		br = mechanize.Browser()
		
		try:
			while True:
				self.scrape_data = urls.get(False, self.timeout)		
				if self.scrape_data.get_depth() < 0: continue
				try:
					response = br.open(self.scrape_data.get_url())
					
					for link in br.links():
						furl = link.url if "http://" in link.url else link.base_url + link.url
						if furl not in visited:
							urls.put(ScrapeData(furl, self.scrape_data.get_depth() - 1))
							visited.add(furl)
					
					html = response.read()
					self.scrape_data.set_content(str(html))
					with r_lock:
						results.append(self.scrape_data.get_content())
						self.scrape_data = None
				except Exception as e:
					print e, self.scrape_data.get_url()
					self.scrape_data = None
		except Empty:
			pass


@task
def crawl(url, maxdepth, topic):
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
	
	return results
	
#crawl("http://stackoverflow.com/questions/4744426/python-threading-with-global-variables", 1, 0)