Introduction
========

This is a distributed python QA system based on mongoDB.

ToDo
=============

* Bash scripts to setup and start a node, server, or monitor
* Implement a research paper writer on top of the crawler QA system
* Create a monitoring API in node.js that runs on each worker and provides a TCP endpoint API for requesting status data, memory, cpu, etc...
* Make QA python program listen for HTTP requests to begin processing, provide API to see progress, get data so far, kill, etc...
  The crawl queue is built into celery.
* Create a frontend in node.js that calls the HTTP endpoint to begin a crawl and then calls multiple APIs to show live data.
  This will be constantly running and will show all live status of current crawl and waiting crawls and provide JS API for web app.
* Start python api server from node
* Persist all queries ever performed, i.e. make all queries searchable, and use as cache.

Contributors
=============

William Schurman

License
========

 Copyright 2011 William Schurman.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.