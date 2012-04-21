$(document).ready(function(){
   
   now.receiveSearchResults = function(res) {
      console.log(res);
      
      var st = "";
      for (var i in res) {
         st += "<li class='result'>"+res[i]._id+" ("+res[i].value+" occurences)</li>";
      }
      
      $("#results").append("<ol class='well'>"+st+"</ol>");
   }

   $("#queryform").submit(function() {
      var s = $("#search").val();
      var req = {
         "search": s
      };

      now.sendSearchRequest(req);
      return false;
   });
});

