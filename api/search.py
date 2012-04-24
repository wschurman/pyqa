import config
import os.path

from bson import objectid
from bson.code import Code
from threading import Thread, Lock

class SearchThread(Thread):
   """
   Thread to handle running MapReduce job on MongoDB collection for a search term.
   """
   
   def __init__(self, key, q):
      self.key = key
      self.q = q
      self.results = None
      Thread.__init__(self)
   
   def run(self):
      """
      Dispatches MapReduce job to MongoDB collection and waits for result.
      """
      map = Code(open(os.path.dirname(__file__) + "/search/map.js", 'r').read().replace("%q%", self.q))
      reduce = Code(open(os.path.dirname(__file__) + "/search/reduce.js", 'r').read())
      
      oid = objectid.ObjectId(self.key)
      
      self.results = config.collection.map_reduce(map, reduce, out="search_collection", query={"_id":oid, "parse_type":"StripTags"})
      
   def get_results(self):
      """ huh """
      ret = list()
      for d in self.results.find():
         ret.append(d)
      return ret
      # return {"dbkey":str(self.resultkey)}