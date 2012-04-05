from bson.code import Code
from threading import Thread, Lock

class SearchThread(Thread):
   """
   Thread to handle running MapReduce job on MongoDB collection for a search term.
   """
   map = Code( "function () {"
               "  this.tags.forEach(function(z) {"
               "    emit(z, 1);"
               "  });"
               "}")
   reduce = Code(    "function (key, values) {"
                     "  var total = 0;"
                     "  for (var i = 0; i < values.length; i++) {"
                     "    total += values[i];"
                     "  }"
                     "  return total;"
                     "}")
   
   def __init__(self, q):
      self.q = q
      self.resultkey = None
      Thread.__init__(self)
   
   def run(self):
      """
      Dispatches MapReduce job to MongoDB collection and waits for result.
      """
      # query mr
      # block until query is complete
      # self.resultkey = results
      
   def get_results(self):
      return {"dbkey":str(self.resultkey)}