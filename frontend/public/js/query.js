$(document).ready(function(){
   
   now.receiveSearchResults = function(res) {
      console.log(res);
      $("#results").append("<div class='well'>"+JSON.stringify(res)+"</div>");
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

