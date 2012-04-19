import config
from bson.code import Code

map = Code(open("search/map.js", 'r').read())
reduce = Code(open("search/reduce.js", 'r').read())

results = config.collection.map_reduce(map, reduce, out="hahah")

for result in results.find():
   print result