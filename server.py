import config
from query import QueryThread
from search import SearchThread

import atexit
import urllib2
from bson import objectid
import psutil, os, time, sys
from threading import Thread, Lock
from bottle import route, run, request, abort, get, post, delete, error, response


# Global datastructures for keeping track of queries
query_threads = dict()
qid_counter = 0
qid_lock = Lock()

# return either waiting, running, or done
# if running, return some sort of status data
# if done, return info necessary to query data from mongoDB
def get_query_status(qid):
   """
   Retrieves the status of the specified query.
   """
   return query_threads[qid].get_status()

@get('/api/status')
def api_status():
   """
   Provides an endpoint for checking if server is up.
   Path: GET /api/status
   """
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
   """
   TODO: Remove
   """
   return "Hello, World!"

@get('/api/queries')
def list_queries():
   """
   Lists all queries executed.
   Path: GET /api/queries
   """
   if len(query_threads) == 0:
      abort(204, "No Queries.")
   retdict = dict()
   for k, v in query_threads.iteritems():
      retdict[k] = v.get_query()
   response.set_header('Content-Type', 'application/json')
   return retdict

@post('/api/queries')
def run_query():
   """
   Creates a new QueryThread to handle the query.
   JSON POST body of the following form required: {"query":"hello", "depth":4}
   Content-type header must be application/json.
   Path: POST /api/queries
   """
   global qid_lock, qid_counter  
   r = request.json
   if not r or not r["query"] or not r["depth"] and not r["depth"] == 0:
      abort(400, "Invalid call, bad request.")
   else:
      with qid_lock:
         qid_counter += 1
         qid = qid_counter
      t = QueryThread(r["query"], int(r["depth"]), qid)
      query_threads[qid] = t
      t.start()
      response.status = "201 Made Query"
      response.set_header('Content-Type', 'application/json')
      return {"query_id":qid}

@get('/api/queries/<qid:int>')
def get_query(qid):
   """
   Retrieves a QueryThread's status.
   Path: GET /api/queries/<query_id>
   """
   if qid not in query_threads:
      abort(404, "Query not found.")
   else:
      # make a thread
      
      # join the thread, kindof blocking but that's okay
      response.set_header('Content-Type', 'application/json')
      return get_query_status(qid)

@get('/api/data/<key>')
def get_data(key):
   """
   Retrieves a QueryThread's data given a specified mongodb key.
   Path: GET /api/data/<key>
   """
   # TODO: Need to make sure the query is finshed
   response.set_header('Content-Type', 'application/json')
   oid = objectid.ObjectId(key)
   res = config.collection.find_one({"_id":oid})
   return json.dumps(res['data'])

@delete('/api/queries/<qid:int>')
def delete_query(qid):
   """
   Stops and deletes a QueryThread.
   Path: DELETE /api/queries/<query_id>
   """
   if not qid in query_threads:
      abort(404, "Query not found.")
   else:
      abort(501, "Not Implemented")
      return "Method Not Implemented"

@get('/api/search/<q>')
def run_search(q):
   """
   Runs a search on tag-stripped parsed results.
   Path: GET /api/search/<q>
   """
   if not q:
      abort(404, "Invalid Query")
   else:
      s = SearchThread(urllib2.unquote_plus(q))
      s.start()
      s.join()
      response.set_header('Content-Type', 'application/json')
      return s.get_results()
      

@get('/api/server_stats')
def get_server_stats():
   """
   Retrieves all server information.
   Path: GET /api/server_stats
   """
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
         'host': config.connection.host,
         'port': config.connection.port,
         'db': config.db.name,
         'collection_name': config.collection.name
      }
   }

# The following method is a catchall method

@error(501)
def error501(error):
   return "API Method Not Implemented"

@error(404)
def error404(error):
    return 'Query or Method Not Found'

run(host=config.get("API_HOST"), port=config.get("API_PORT"))

@atexit.register
def goodbye():
   config.mqconnection.close()
   config.connection.close()
   print "PyQA says goodbye."