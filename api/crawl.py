# Requires: celery, mechanize, beautifulsoup, lxml
from celery.task import task
from celery.task.sets import subtask
from threading import Thread, Lock
from Queue import Queue, Empty
import re
import mechanize
import os, time
from parse import parse
from urlparse import urljoin

visited = set()
valids = []

class ScraperWorker(Thread):
	"""
	Thread to handle scraping of a url. Distributes link scraping and parsing as tasks and subtasks
	to celery clients. Also creates child threads for each link found on url.
	"""
	def __init__(self, url, depth, parser):
		self.url = url
		self.depth = depth
		self.parser = parser
		Thread.__init__(self)
		
	def run(self):
		"""
		Dispatches crawl/parse async celery call, creates child threads.
		"""
		global visited, valids
		
		#child ScraperWorker threads
		subworkers = []
		
		
		self.async_result = get_content.apply_async(args=[self.url, parse.subtask((self.parser, ))], serializer="json", expires=20)
		
		# get first result to extract links
		while not self.async_result.ready():
			time.sleep(0)
		
		# no first result, die
		if not self.async_result.successful() or self.async_result.result == None:
			return
		
		# print self.url, "Got first result"
		# add visited url
		result = self.async_result.result
		visited.add(self.url)
		
		# if need to, create workers for found links
		if self.depth > 0:
			tovisit = set(result["links"])
			tovisit.difference_update(visited)
		
			for url in tovisit:
				# print "Adding worker for ", url
				w = ScraperWorker(url, self.depth - 1, self.parser)
				w.start()
				subworkers.append(w)
		
		# get the parse subtask from this ScraperWorker's page
		subtask = result["subtask"]
		while not subtask.ready():
			time.sleep(0)
		
		# could not parse, no need to add it to overall result
		if not subtask.successful() or subtask.result == None:
			return
		
		# print self.url, "Got parse subtask and append"
		subresult = subtask.result # dict of k, v parsed and original crawl data
		valids.append(subresult)
		
		# join all sub link workers
		for worker in subworkers:
			worker.join()
		
		# print self.url, "Joined all subworkers"


@task
def crawl(url, maxdepth, parser):
	"""
	Creates a ScraperWorker for url, crawling at a depth of maxdepth,
	and using parser as the parser
	"""
	global visited, valids
	if maxdepth < 0: return -1
	
	visited.add(url)
	
	r = ScraperWorker(url, maxdepth, parser)
	r.start()
	r.join()
	
	return valids

@task
def get_content(url, callback=None):
	"""
	Opens the url, scrapes the links, returns a dict of 
	values as well as a parse subtask called on the results
	"""
	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.set_handle_referer(False)
	try:
		response = br.open(url)
	except:
		raise mechanize.URLError(url)
	final_links = []
	for link in br.links():
		furl = urljoin(url, link.url) #TODO: fix
		final_links.append(furl)
	html = response.read()
	ret = {"links":final_links}
	resp = {"url": url, "links": final_links, "html":str(''.join([x for x in html if ord(x) < 128]))}
	if callback is not None:
		ret["subtask"] = subtask(callback).apply_async(args=[resp], serializer="json", expires=20)
	return ret # opened successfully
		