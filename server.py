from crawl import crawl
from parse import parse

import json
import time
from threading import Thread
from bottle import route, run, request, abort, get, post

class MonitorThread(Thread):
	
	def __init__(self, q):
		self.query = q
	
	def run(self):
		self.crawl_async_result = crawl.delay(self.query)
		while not self.crawl_async_result.ready():
			time.sleep(0)
		self.parse_async_result = parse.delay(self.crawl_async_result.result, "keyword")
		while not self.parse_async_result.ready():
			time.sleep(0)
		
		insert_into_db(self.parse_async_result.result)
	
	def insert_into_db(data):
		pass


@get('/hello')
def hello():
	return "hello world"

@get('/api/query/<q>')
def run_query(q):
	if not q:
		abort(404, "Invalid query.")
	else:
		t = MonitorThread(q)
		t.start()

@get('/api/<fn>')
def api_call(fn):
	if not fn:
		abort(404, "Invalid API function.")


run(host='localhost', port=1337)