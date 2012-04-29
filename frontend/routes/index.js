
/*
 * GET home page.
 */

exports.index = function(req, res){
  res.render('index', { title: 'Dashboard' })
};

exports.about = function(req, res){
  res.render('about', { title: 'About' })
};