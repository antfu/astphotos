'use strict';

/* =============== Vue Directive ===============*/
Vue.directive('scrollable', function(){
  var el = $(this.el);
  el.bind('mousewheel DOMMouseScroll', scroll.scrollwheel);
});
Vue.directive('modal-image', function (id) {
  var vm = this.vm;
  var pic = $(this.el).removeClass('horizontal vertical');
  var modal_data = vm.$data.current.photos[id];
  var screen_aspect = $(window).width() / $(window).height();
  var image_aspect = modal_data.width / modal_data.height;
  if (screen_aspect <= image_aspect)
  {
    pic.addClass('horizontal');
    pic.css('left',0);
    pic.css('top',($(window).height() - modal_data.height / modal_data.width * $(window).width())/2);
  }
  else
  {
    pic.addClass('vertical');
    pic.css('top',0);
    pic.css('left',($(window).width() - modal_data.width / modal_data.height * $(window).height())/2);
  }
  pic.attr('src',modal_data.path);
});

/* =============== Vue Objects ===============*/

var vue_mix = {
  methods: {
    scroll: function(i) {
      scroll.scroll(i);
    },
    scrolltop: function() {
      body_scroll_to(0);
    },
    window_width: function() {
      return $(window).width();
    }
  }
}

/* =============== Events ===============*/
var on_gallery_expand = function(album) {
  scroll.reset();
  resize_nav();
  body_scroll_to(0);
}
var on_gallery_collapse = function() {
  resize_nav();
  body_scroll_to(0);
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
  var vertical = scroll.vertical();
  if (vertical)
    scroll.scrolling = true;
  to = to || 0;
  $('body').animate({
     scrollTop: to,
  }, Math.abs($('body').scrollTop()-to) / 1.5, function() {
    if (vertical)
      scroll.scrolling = false;
    if (on_complete)
      on_complete();
  });
}

var scroll = {
  el: function () { return $('#scroller'); },
  vertical: function () {
    if (full_data.current)
      return full_data.current.gallery_mode || 0;
    return 0
  },
  key: function() {
    if (scroll.vertical())
      return 'scrollTop';
    else
      return 'scrollLeft';
  },
  scrolling: false,
  current: function(){
    scroll.el().scrollLeft.apply(this, arguments);
  },
  offsets: function () {
    var result = [];
    if (scroll.vertical())
      $('.gallery .photo').each(function(i,e){result.push($(e).offset().top - $('body').scrollTop())});
    else
      $('.gallery .photo').each(function(i,e){result.push($(e).offset().left)});
    return result;
  },
  scroll: function (direction) {
    var offsets = scroll.offsets();
    var target_index = scroll.nesrest() + direction;
    if (target_index < 0 || target_index >= offsets.length)
      return;

    scroll.to(target_index,direction);
  },
  to: function (index,direction) {
    if (scroll.vertical())
    {
      if (index < 0 || index >= $('.gallery .photo').length)
        return;
      var target = $($('.gallery .photo')[index]).offset().top;
      if (direction == -1 && !$('.nav').hasClass('hidden'))
        target -= $('.nav').outerHeight();
      if (index == 0)
        target = 0;
      body_scroll_to(target);
    }
    else
    {
      var offsets = scroll.offsets();
      if (index < 0 || index >= offsets.length)
        return;

      var target = offsets[index] + scroll.el().scrollLeft();
      var distance = Math.abs(offsets[index]);

      scroll.scrolling = true;
      scroll.el().animate({
        scrollLeft: target,
      }, distance / 2, function() {
        scroll.scrolling = false;
        scroll.update();
      });
    }
  },
  reset: function () {
    var key = scroll.key();
    var el = scroll.vertical() ? $('body') : scroll.el();
    if (!el[key]()) return;
    var target_obj = {};
    target_obj[key] = 0;
    scroll.scrolling = true;
    el.animate(target_obj, (el[key]() || 0) / 6, function() {
      scroll.scrolling = false;
    });
  },
  nesrest: function () {
    var offsets = scroll.offsets();
    var min_value;
    var min_index = 0;
    for (var i = 0; i < offsets.length; i++) {
      var value = Math.abs(offsets[i]);
      if (min_value === undefined || min_value > value){
        min_index = i;
        min_value = value;
      }
    }
    return min_index;
  },
  update: function () {
    Vue.set(full_data.current,'page',scroll.nesrest()+1);
  },
  scrollwheel: function (e) {
    if (scroll.scrolling) {
      e.preventDefault();
      return;
    }
    e = window.event || e;
    var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));
    var direction = 0;
    if (scroll.vertical())
    {
      if (delta == 0)
        return;
      else if (delta < 0)
        direction = 1;
      else
        direction = -1;
      if (scroll.nesrest() < $('.gallery .photo').length -1)
        e.preventDefault();
      scroll.scroll(direction);
    }
    else
    {
      if (delta == 0)
        return;
      else if (delta < 0)
      {
        if (scroll.el().scrollLeft() >= (scroll.el()[0].scrollWidth - scroll.el().width()))
          return
        direction = 1;
      }
      else
      {
        if (scroll.el().scrollLeft() <= 0)
          return;
        direction = -1;
      }
      e.preventDefault();
      scroll.scroll(direction);
      body_scroll_to(0);
    }
  }
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

  if (scroll.vertical())
    scroll.update();
});

// Disable contextmenu
if (!DEBUG) $('body').contextmenu(function(e) { e.preventDefault(); });

$(function() {
  resize_nav();
});
