
/**
* Module dependencies.
*/

var express = require('express')
, routes = require('./routes')
, nowjs = require('now')
, api = require('request')
, spawn = require('child_process').spawn;
var port = process.env.PORT || 3000;

var app = module.exports = express.createServer();
var everyone = nowjs.initialize(app);

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

// Now.js

everyone.now.sendCrawlRequest = function(req) {
   var me = this;
   // send out api call to pyqa api server
   var opts = {
      url: "http://localhost:1337/api/queries",
      json: req
   };

   api.post(opts, function(err, resp, body) {
   	if (!err && resp.statusCode == 201) {
   	   me.now.receiveRequestResponse(body);
   	} else {
   	   me.now.receiveRequestResponse(err);
   	}
   });
};

everyone.now.sendDeleteRequest = function(req) {
   // send out api delete call
};

// CPU Usage with now.js

String.prototype.trim = function() {
   return this.replace(/^\s+|\s+$/g,"");
}

var output = function(output_data) {
   var output_array = output_data.toString().trim().split(/\s+/);
   for (var i=0; i < output_array.length; i++) {
      output_array[i] = parseFloat( output_array[i]);
   };
   output_hash = {
      date:new Date(),
      cpu:{
         us:output_array[3],
         sy:output_array[4],
         id:output_array[5]
      }
   };

   try {
      everyone.now.receiveMonitorUpdate(output_hash);
   } catch(e) {

   }
};

var iostat = spawn('iostat', ["-w 1"]);
iostat.stdout.on('data', output);

app.listen(port);
console.log("Express server listening on port %d in %s mode", app.address().port, app.settings.env);
