import pika
import json
import pymongo
from pymongo import Connection

# load cross language config
cfile = open('pyqaconfig.json')
config = json.load(cfile)
cfile.close()

def cf(key):
   """
   Gets a config value, removes unicode if necessary.
   """
   if isinstance(config[key], int):
      return config[key]
   else:
      return str(config[key])
      
def get(key):
   return cf(key)


# Connect to MongoDB
try:
   connection = Connection(cf("LOCAL"), 27017)
except Exception:
   try:
      connection = Connection(cf("EC2"), 27017)
   except Exception:
      print "No MongoDB connection available. Exiting."
      sys.exit(1)

db = connection[cf("MONGO_DB")]
collection = db[cf("MONGO_COLLECTION")]

# Connect to RabbitMQ
mqcredentials = pika.PlainCredentials(cf("MQUSER"), cf("MQPASS"))
mqconnection = pika.BlockingConnection(pika.ConnectionParameters(
        host=cf("EC2"), port=cf("MQPORT"), virtual_host=cf("MQVHOST"), credentials=mqcredentials))
mqchannel = mqconnection.channel()
mqchannel.exchange_declare(exchange=cf("MQEXCHANGE"), type='fanout', durable=True, auto_delete=False)