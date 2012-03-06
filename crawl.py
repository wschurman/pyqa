# Requires: celery, mechanize, beautifulsoup, lxml
from celery.task import task
from celery.task.sets import subtask
from threading import Thread, Lock
from Queue import Queue, Empty
import re
import mechanize
import os, time
from parse import parse

visited = set()
valids = []

class ScraperWorker(Thread):
	
	def __init__(self, url, depth, parser):
		self.url = url
		self.depth = depth
		self.parser = parser
		Thread.__init__(self)
		
	def run(self):
		global visited, valids
		
		subworkers = []
		
		self.async_result = get_content.apply_async(args=[self.url, parse.subtask((self.parser, ))], serializer="json")
		
		# get first result to extract links
		while not self.async_result.ready():
			time.sleep(0)
		
		# no first result, die
		if not self.async_result.successful() or self.async_result.result == None:
			return
		
		# add visited url
		result = self.async_result.result
		visited.add(self.url)
		
		# if need to, create workers for found links
		if self.depth > 0:
			tovisit = result["links"]
			tovisit = set(tovisit).difference(visited)
		
			for url in tovisit:
				w = ScraperWorker(url, self.depth - 1, self.parser)
				w.start()
				subworkers.append(w)
		
		# get the parse subtask
		subtask = result["subtask"]
		while not subtask.ready():
			time.sleep(0)
		
		# could not parse, no need to add it to overall result
		if not subtask.successful() or subtask.result == None:
			return
		
		subresult = subtask.result # dict of k, v parsed and original crawl data
		valids.append(subresult)
		
		# join all sub link workers
		for worker in subworkers:
			worker.join()


@task
def crawl(url, maxdepth, parser):
	global visited, valids
	if maxdepth == 0: return -1
	
	visited.add(url)
	
	r = ScraperWorker(url, maxdepth, parser)
	r.start()
	r.join()
	
	return valids

@task
def get_content(url, callback=None):
	br = mechanize.Browser()
	try:
		response = br.open(url)
		final_links = []
		for link in br.links():
			furl = link.url if "http://" in link.url else link.base_url + link.url #TODO: fix
			final_links.append(furl)
		html = response.read()
		ret = {"links":final_links}
		resp = {"url": url, "links": final_links, "html":str(html)}
		if callback is not None:
			ret["subtask"] = subtask(callback).apply_async(args=[resp], serializer="json")
		return ret # opened successfully
	except Exception as e:
		print e, url
		return None
		