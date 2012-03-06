from crawl import crawl
from parse import parse

import json
import time
import pymongo
import psutil, os
from threading import Thread, Lock
from bottle import route, run, request, abort, get, post, delete, error, response

from pymongo import Connection

try:
	connection = Connection('localhost', 27017)
except Exception:
	connection = Connection('ec2-184-73-79-244.compute-1.amazonaws.com', 27017)

db = connection.query_db
collection = db.query_collection

query_threads = dict()
qid_counter = 0
qid_lock = Lock()

class QueryThread(Thread):
	
	def __init__(self, q, d, qid):
		self.query = q
		self.start_url = "http://www.google.com/search?q=" + q
		self.max_depth = d
		self.qid = qid
		self.qstatus = "Waiting"
		self.crawlstatus = None
		self.parsestatus = None
		self.dbkey = None
		Thread.__init__(self)
	
	def run(self):
		self.qstatus = "Running"
		self.crawl_async_result = crawl.delay(self.start_url, self.max_depth)
		while not self.crawl_async_result.ready():
			time.sleep(0)
		self.crawlstatus = "Done"
		self.parse_async_result = parse.delay(self.crawl_async_result.result, "keyword")
		while not self.parse_async_result.ready():
			time.sleep(0)
		self.parsestatus = "Done"
		
		insert_into_db(self.parse_async_result.result)
	
	def insert_into_db(self, data):
		global collection
		self.dbkey = collection.insert(data)
		self.qstatus = "Done"
	
	def get_query(self):
		return self.query
	
	def get_status(self):
		return {"status":self.qstatus, "crawlstatus":self.crawlstatus, "parsestatus":self.parsestatus, "dbkey":self.dbkey}

# return either waiting, running, or done
# if running, return some sort of status data
# if done, return info necessary to query data from mongoDB
def get_query_status(qid):
	return json.dumps(query_threads[qid].get_status())

@get('/api/status')
def apistatus():
	#global connection
	status = True
	#status &= connection.server_info()
	return "ok"

@get('/api/hello')
def hello():
	return "Hello, World!"

@get('/api/queries')
def list_queries():
	if len(query_threads) == 0:
		abort(204, "No Queries.")
	retdict = dict()
	for k, v in query_threads.iteritems():
		retdict[k] = v.get_query
	response.set_header('Content-Type', 'application/json')
	return json.dumps(retdict)

# call with a query and depth json field in the post body, e.g. {"query":"hello", "depth":4}
@post('/api/queries')
def run_query():
	global qid_lock, qid_counter	
	r = request.json
	print r
	if not r or not r["query"] or not r["depth"]:
		abort(400, "Invalid call, bad request.")
	else:
		with qid_lock:
			qid_counter += 1
			qid = qid_counter
		t = QueryThread(r.query, r.depth, qid)
		query_threads[qid] = t
		t.start()
		response.status_code = 201
		response.set_header('Content-Type', 'application/json')
		return json.dumps({"query_id":qid})

@get('/api/queries/<qid>')
def get_query(qid):
	if not qid in query_threads:
		abort(404, "Query not found.")
	else:
		response.set_header('Content-Type', 'application/json')
		return get_query_status(qid)


@delete('/api/queries/<qid>')
def delete_query(qid):
	if not qid in query_threads:
		abort(404, "Query not found.")
	else:
		abort(501, "Not Implemented")
		return "Method Not Implemented"

@get('/api/server_stats')
def get_server_stats():
	p = psutil.Process(os.getpid())
	response.set_header('Content-Type', 'application/json')
	return json.dumps({
		"num_threads":p.get_num_threads(),
		"cpu_percent":p.get_cpu_percent(interval=0),
		"memory":p.get_memory_info(),
		"connections":p.get_connections(kind='all')
	})

# The following method is a catchall method

@error(501)
def error501(error):
	return "API Method Not Implemented"

@error(404)
def error404(error):
    return 'Unknown API method'

run(host='0.0.0.0', port=1337)