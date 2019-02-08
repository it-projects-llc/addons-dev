$(document).ready(function() {
  $("header .navbar-default .navbar-nav > li").mouseenter(function(){
    var self = $(this);
    self.addClass('dark');
    $('header .navbar-default .navbar-nav > li').addClass('light');
  });

  $("header .navbar-default .navbar-nav > li").mouseleave(function(){
    var self = $(this);
    $('header .navbar-default .navbar-nav > li').removeClass('light');
    self.removeClass('dark');
  });
  
});