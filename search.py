import config

from bson.code import Code
from threading import Thread, Lock

class SearchThread(Thread):
   """
   Thread to handle running MapReduce job on MongoDB collection for a search term.
   """
   
   def __init__(self, q):
      self.q = q
      self.results = None
      Thread.__init__(self)
   
   def run(self):
      """
      Dispatches MapReduce job to MongoDB collection and waits for result.
      """
      map = Code(open("search/map.js", 'r').read().replace("%q%", self.q))
      reduce = Code(open("search/reduce.js", 'r').read())
      
      self.results = config.collection.map_reduce(map, reduce, out="search_collection", query={"parse_type":"strip"})
      
   def get_results(self):
      """ huh """
      ret = list()
      for d in self.results.find():
         ret.append(d)
      return ret
      # return {"dbkey":str(self.resultkey)}