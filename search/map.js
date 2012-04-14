function () {
   this.data.forEach(function(elem) {
      elem.parse_results.split(' ').forEach(function(word) {
         if (word.toLowerCase() == '%q%') {
            emit(elem.url, 1);
         }
      });
   });
}