import config

from crawl import crawl
from parse import parse

import time, json
from threading import Thread, Lock

class QueryThread(Thread):
   """
   Thread to handle a query request. Used to create, monitor, and retain accessor 
   information of a crawl request.
   """
   def __init__(self, q, d, qid):
      self.query = q
      self.start_url = q
      self.max_depth = d
      self.qid = qid
      self.parser = "StripTags"
      self.qstatus = "Waiting"
      self.crawlstatus = None
      self.dbkey = None
      Thread.__init__(self)
      
   def run(self):
      """
      Dispatches all async celery crawl/parse requests and waits for result.
      Inserts result into mongodb.
      """
      print "CAlled run in querythread"
      #global config.mqchannel
      self.qstatus = "Running"
      self.crawl_async_result = crawl.apply_async(args=[self.start_url, self.max_depth, self.parser], serializer="json")
      while not self.crawl_async_result.ready():
         time.sleep(0)
      
      # self.crawl_async_result is a list of { URLs, links, htmls } to be parsed
      
      self.crawlstatus = "Done"
      print "Crawl Done"
      print json.dumps(self.crawl_async_result.result, indent=4)
      
      self.__insert_into_db(self.crawl_async_result.result)
      content = json.dumps({"query_id":self.qid, "message":"done", "dbkey":str(self.dbkey)});
      config.mqchannel.basic_publish(exchange=config.get("MQEXCHANGE"), routing_key='', body=content)
      
   
   def __insert_into_db(self, data):
      #global config.collection, config.mqchannel
      self.dbkey = config.collection.insert({"data":data, "parse_type":self.parser})
      self.qstatus = "Done"
   
   def get_query(self):
      return self.query
   
   def get_status(self):
      return {"query_id":self.qid, "status":self.qstatus, "crawlstatus":self.crawlstatus, "dbkey":str(self.dbkey)}
   
