'use strict';

/* =============== Vue Directive ===============*/


/* =============== Vue Objects ===============*/

var vue_mix = {
  methods: {
    scrolltop: function() {
      body_scroll_to(0);
    },
    window_width: function() {
      return $(window).width();
    }
  }
}

/* =============== Events ===============*/
var on_gallery_expand = function() {
  body_scroll_to(0);
}
var on_gallery_collapse = function() {
  body_scroll_to(0);
}
var on_router_changed = function() {
  resize_nav();
}

/* =============== Functions ===============*/
function immediate_and_timeout(func,timeout) {
  func();
  if (timeout == undefined)
    timeout = 100;
  return setTimeout(func,timeout);
}
function resize_nav() {
  immediate_and_timeout(function () {
    $('.nav-space').height($('.nav').outerHeight());
  },100);
}

function body_scroll_to(to, on_complete) {
  to = to || 0;
  $('body').animate({
     scrollTop: to,
  }, Math.abs($('body').scrollTop()-to) / 1.5, function() {
    if (on_complete)
      on_complete();
  });
}

var lastScrollTop = 0;
$(window).scroll(function() {
  if ($(window).scrollTop() > 500)
    $('#scrolltop_btn').removeClass('hidden');
  else
    $('#scrolltop_btn').addClass('hidden');

  var st = $(this).scrollTop();
  if (st < lastScrollTop){
    // upscroll
    $('.nav').removeClass('hidden');
  } else {
    // downscroll
    if ($(window).scrollTop() > 300 )
      $('.nav').addClass('hidden');
  }
  lastScrollTop = st;
});

// Disable contextmenu
if (!DEBUG) $('body').contextmenu(function(e) { e.preventDefault(); });

$(function() {
  resize_nav();
});
