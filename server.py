from crawl import crawl
from parse import parse

import json
import time
from threading import Thread, Lock
from bottle import route, run, request, abort, get, post, delete, error

query_threads = dict()
qid_counter = 0
qid_lock = Lock()

class MonitorThread(Thread):
	
	def __init__(self, q, d, qid):
		self.start_url = "http://www.google.com/search?q=" + q
		self.max_depth = d
		self.qid = qid
		Thread.__init__(self)
	
	def run(self):
		self.crawl_async_result = crawl.delay(self.start_url, self.max_depth)
		while not self.crawl_async_result.ready():
			time.sleep(0)
		self.parse_async_result = parse.delay(self.crawl_async_result.result, "keyword")
		while not self.parse_async_result.ready():
			time.sleep(0)
		
		insert_into_db(self.parse_async_result.result)
	
	def insert_into_db(data):
		pass

def get_query_status(qid):
	return json.dumps({ "this is a fake" : "query status" })
	
def make_json(status, data):
	return json.dumps({ 'status' : status, 'data' : data });

@get('/api/status')
def apistatus():
	pass

@get('/api/hello')
def hello():
	return "hello world"

@get('/api/queries')
def list_queries():
	return "Method Not Implemented"

@post('/api/queries')
def run_query():
	global qid_lock, qid_counter	
	r = request.json
	print r
	if not r or not r["query"] or not r["depth"]:
		abort(404, "Invalid call.")
	else:
		return "started monitor thread"
		with qid_lock:
			qid_counter += 1
			qid = qid_counter
		t = MonitorThread(r.query, r.depth, qid)
		query_threads[qid] = t
		t.start()
		response.set_header('Content-Type', 'application/json')
		return make_json("ok", {"query_id":qid})

@get('/api/queries/<qid>')
def get_query(qid):
	if not qid in query_threads:
		abort(404, "Query not found.")
	else:
		response.set_header('Content-Type', 'application/json')
		return make_json('ok', get_query_status(qid)) # TODO: write get_query_status


@delete('/api/queries/<qid>')
def delete_query(qid):
	if not qid in query_threads:
		abort(404, "Query not found.")
	else:
		return "Method Not Implemented"

@get('/api/server_stats')
def get_server_stats():
	return "Method Not Implemented"

# The following method is a catchall method

@error(404)
def error404(error):
    return 'Unknown API method'

run(host='localhost', port=1337)