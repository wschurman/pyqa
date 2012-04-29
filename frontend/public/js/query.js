$(document).ready(function(){
   
   now.receiveSearchResults = function(res) {
      console.log(res);
      
      var st = "";
      for (var i in res) {
         st += "<li class='result'><a href='"+res[i]._id+"'>"+res[i]._id+"</a> ("+res[i].value+" occurences)</li>";
      }
      
      $("#results").prepend("<ol class='well'>"+st+"</ol>");
   }

   $("#queryform").submit(function() {
      var s = $("#search").val();
      var id = $("#qid").val();
      var req = {
         "search": s,
         "id": id
      };

      now.sendSearchRequest(req);
      return false;
   });
});

