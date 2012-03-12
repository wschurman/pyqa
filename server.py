from crawl import crawl
from parse import parse

import json
import pymongo
from bson import objectid
import psutil, os, time
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
		self.start_url = q
		self.max_depth = d
		self.qid = qid
		self.qstatus = "Waiting"
		self.crawlstatus = None
		self.dbkey = None
		Thread.__init__(self)
	
	def run(self):
		self.qstatus = "Running"
		self.crawl_async_result = crawl.apply_async(args=[self.start_url, self.max_depth, "keyword"], serializer="json")
		while not self.crawl_async_result.ready():
			time.sleep(0)
		
		# self.crawl_async_result is a list of { URLs, links, htmls } to be parsed
		
		self.crawlstatus = "Done"
		# print "Crawl Done"
		print json.dumps(self.crawl_async_result.result, indent=4)
		
		self.__insert_into_db(self.crawl_async_result.result)
	
	def __insert_into_db(self, data):
		global collection
		self.dbkey = collection.insert({"data":data})
		self.qstatus = "Done"
	
	def get_query(self):
		return self.query
	
	def get_status(self):
		return {"status":self.qstatus, "crawlstatus":self.crawlstatus, "dbkey":str(self.dbkey)}

# return either waiting, running, or done
# if running, return some sort of status data
# if done, return info necessary to query data from mongoDB
def get_query_status(qid):
	return query_threads[qid].get_status()

@get('/api/status')
def api_status():
	#global connection
	status = True
	#status &= connection.server_info()
	response.set_header('Content-Type', 'application/json')
	return {
		'status':'online',
		'servertime':time.time(),
	}

@get('/api/hello')
def hello():
	return "Hello, World!"

@get('/api/queries')
def list_queries():
	if len(query_threads) == 0:
		abort(204, "No Queries.")
	retdict = dict()
	for k, v in query_threads.iteritems():
		retdict[k] = v.get_query()
	response.set_header('Content-Type', 'application/json')
	return retdict

# call with a query and depth json field in the post body, e.g. {"query":"hello", "depth":4}
@post('/api/queries')
def run_query():
	global qid_lock, qid_counter	
	r = request.json
	if not r or not r["query"] or not r["depth"] and not r["depth"] == 0:
		abort(400, "Invalid call, bad request.")
	else:
		with qid_lock:
			qid_counter += 1
			qid = qid_counter
		t = QueryThread(r["query"], r["depth"], qid)
		query_threads[qid] = t
		t.start()
		response.status = "201 Made Query"
		response.set_header('Content-Type', 'application/json')
		return {"query_id":qid}

@get('/api/queries/<qid:int>')
def get_query(qid):
	if qid not in query_threads:
		abort(404, "Query not found.")
	else:
		response.set_header('Content-Type', 'application/json')
		return get_query_status(qid)

@get('/api/data/<key>')
def get_data(key):
	response.set_header('Content-Type', 'application/json')
	oid = objectid.ObjectId(key)
	res = collection.find_one({"_id":oid})
	return json.dumps(res['data'])

@delete('/api/queries/<qid:int>')
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
	return {
		'status':'online',
		'servertime':time.time(),
		"num_threads":p.get_num_threads(),
		"cpu_percent":p.get_cpu_percent(interval=0),
		"memory":p.get_memory_info(),
		"connections":p.get_connections(kind='all'),
		'mongodb': {
			'host': connection.host,
			'port': connection.port,
			'db': db.name,
			'collection_name': collection.name
		}
	}

# The following method is a catchall method

@error(501)
def error501(error):
	return "API Method Not Implemented"

@error(404)
def error404(error):
    return 'Query or Method Not Found'

run(host='0.0.0.0', port=1337)