
/**
* Module dependencies.
*/

var express = require('express')
, routes = require('./routes')
, nowjs = require('now')
, api = require('request')
, amqp = require('amqp')
, spawn = require('child_process').spawn
, mongo = require('mongoskin');

// Load global config
var config = require('../pyqaconfig.json');
var apiuri = function(method) {
   return "http://"+config.LOCAL+":"+config.API_PORT+"/api/"+method;
}

// Start express, now
var port = process.env.PORT || config.FRONTEND_PORT;
var app = module.exports = express.createServer();
var everyone = nowjs.initialize(app);

// Connect to MongoDB

var ObjectID = mongo.ObjectID;
var mdb = mongo.db(config.EC2+':27017/'+config.MONGO_DB);
var collection = mdb.collection(config.MONGO_COLLECTION);

// Start RabbitMQ
var mqconnection = amqp.createConnection({
   host: config.EC2,
   port: config.MQPORT,
   login: config.MQUSER,
   password: config.MQPASS,
   vhost: config.MQVHOST
});

// Configuration
app.configure(function(){
   app.set('views', __dirname + '/views');
   app.set('view engine', 'jade');
   app.use(express.bodyParser());
   app.use(express.methodOverride());
   app.use(app.router);
   app.use(express.static(__dirname + '/public'));
});

app.configure('development', function(){
   app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
});

app.configure('production', function(){
   app.use(express.errorHandler());
});

// Routes

app.get('/', routes.index);
app.get('/docs', routes.docs);
app.get('/about', routes.about);
app.get('/query', routes.query);
app.get('/data/:id', function(req, res){
   getData(req.params.id, function(dat) {
      console.log(dat);
      if (dat.err) {
         res.send('huh?', 404);
      } else {
         res.render('data', { title: 'Data', d:dat.doc.data }) 
      }
   });
});

// Now.js

var requests = {};

everyone.now.sendCrawlRequest = function(req) {
   var me = this;
   // send out api call to pyqa api server
   var opts = {
      url: apiuri("queries"),
      json: req
   };

   api.post(opts, function(err, resp, body) {
   	if (!err && resp.statusCode == 201) {
   	   requests[body.query_id] = {
   	      ev: me,
   	      req: req
   	   };
   	   me.now.receiveRequestResponse(body);
   	} else {
   	   me.now.receiveRequestResponse(err);
   	}
   });
};

search_sort = function(a, b) {
   return (b.value - a.value);
}

everyone.now.sendSearchRequest = function(req) {
   var me = this;
   // send out api call to pyqa api server
   var opts = {
      url: apiuri("search/"+req.search)
   };

   api.get(opts, function(err, resp, body) {
   	if (!err && resp.statusCode == 200) {
   	   var p = JSON.parse(body);
   	   p.sort(search_sort);
   	   me.now.receiveSearchResults(p);
   	} else {
   	   me.now.receiveSearchResults(err);
   	}
   });
};

everyone.now.sendDeleteRequest = function(req) {
   // send out api delete call
};

getData = function(key, cb) {
   // query mongo
   
   var id = null;
   try {
      id = new ObjectID(key);
   } catch (e) {
      cb({
         err: "Invalid key"
      });
      return;
   }
   
   collection.findOne({_id:new ObjectID(key)}, function(err, doc) {
      cb({
         err: err,
         doc: doc
      });
   });
}

// CPU Usage with now.js

String.prototype.trim = function() {
   return this.replace(/^\s+|\s+$/g,"");
}

var fst = true;
var start_index = 0;

var output = function(output_data) {
   if (fst) {
      var numdisk = output_data.toString().trim().match(/disk/g).length;
      start_index = numdisk * 3;
      fst = false;
      return;
   }
   
   var output_array = output_data.toString().trim().split(/\s+/);

   for (var i=0; i < output_array.length; i++) {
      output_array[i] = parseFloat( output_array[i]);
   };

   output_hash = {
      date:new Date(),
      cpu:{
         us:output_array[start_index],
         sy:output_array[start_index+1],
         id:output_array[start_index+2]
      }
   };

   try {
      everyone.now.receiveMonitorUpdate(output_hash);
   } catch(e) {
      
   }
};

var iostat = spawn('iostat', ["-w 1"]);
iostat.stdout.on('data', output);

var deliverMessage = function(m) {
   if (m.query_id) {
      getData(m.dbkey, function(d) {
         requests[m.query_id].ev.now.receiveResults(d.doc.data);
      });
   } else {
      everyone.now.receiveMessage(m);
   }
}

mqconnection.on('ready', function() {
   var q = mqconnection.queue(config.MQQUEUE, {durable:true, autoDelete:false});
   q.bind(config.MQEXCHANGE);
   q.subscribe(function (message, headers, deliveryInfo) {
      var p = JSON.parse(message.data.toString());
      console.log(p);
      deliverMessage(p);
   });
});

app.listen(port);
console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);

process.on('SIGTERM', function() {
   iostat.kill();
});