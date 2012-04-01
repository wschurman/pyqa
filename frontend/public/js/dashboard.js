$(document).ready(function(){

   var smoothie = new SmoothieChart();
   smoothie.streamTo(document.getElementById("cpucanvas"), 1000);

   var line_id = new TimeSeries();
   var line_sy = new TimeSeries();
   var line_us = new TimeSeries();

   smoothie.addTimeSeries(line_id, { strokeStyle:'rgb(0, 0, 255)', lineWidth:2 });
   smoothie.addTimeSeries(line_sy, { strokeStyle:'rgb(255, 0, 0)', lineWidth:2 });
   smoothie.addTimeSeries(line_us, { strokeStyle:'rgb(0, 255, 0)', lineWidth:2 });

   now.receiveMonitorUpdate = function(st) {
      var t = new Date().getTime();
      line_id.append(t, st.cpu.id);
      line_sy.append(t, st.cpu.sy);
      line_us.append(t, st.cpu.us);
   }

   now.receiveRequestResponse = function(resp) {
      console.log(resp);
   }
   
   now.receiveResults = function(res) {
      console.log(res);
   }

   $("#reqform").submit(function() {
      var url = $("#url").val();
      var depth = $("#depth").val();
      var req = {
         "query": url,
         "depth": depth
      };

      now.sendCrawlRequest(req);
      return false;
   });
});

