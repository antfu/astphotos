Vue.config.debug = true;
Vue.config.delimiters = ['${', '}'];
var full_data = {};
var gallery_photo_resized = true;
var gallery_photo_height = 0;

Vue.directive('square-image',{
  bind:function(){
    var pic = $(this.el);
    this.el.onload = function(){
      if (pic.height() > pic.width())
        pic.css('width','100%');
      else
        pic.css('height','100%');
      pic.css('opacity',1);
    };
  }
});
Vue.directive('full-photo',{
  bind:function(){
    var pic = $(this.el);
    this.el.onload = function(){
      pic.css('opacity',1);
    };
  }
});
var vue_inst_nav = new Vue({
  el: '#nav',
  data: full_data,
  methods:
  {
    collapse: gallery_collapse
  }
});
var vue_inst_albums = new Vue({
  el: '#albums',
  data: full_data,
  methods: {
    expand: function (album) {
      if (full_data.viewmode == 0 || full_data.current != album)
        gallery_expend(album);
      else
        gallery_collapse();
    }
  }
});
var vue_inst_gallery = new Vue({
  el: '#gallery',
  data: full_data,
  methods: {
    photo_height: get_gallery_photo_height
  }
});

$.getJSON('/static/struct.json',function(data){
  full_data = data;
  vue_inst_nav.$data = full_data;
  vue_inst_albums.$data = full_data;
  vue_inst_gallery.$data = full_data;
  update_title();
})


function update_title() {
  if (full_data.viewmode == 0)
    document.title = full_data.title;
  else if (full_data.current) {
    document.title = full_data.current.name + ' - ' +full_data.title;
  }
}
function get_gallery_photo_height() {
  if (!gallery_photo_resized)
    return gallery_photo_height;
  var temp = $('<div class="gallery" class="opacity:0"><div class="photo"></div></div>').appendTo('body');
  gallery_photo_height = temp.find('.photo').height() + 50;
  gallery_photo_resized = false;
  temp.remove();
  return gallery_photo_height;
}

function gallery_expend(album) {
  Vue.set(full_data,'current',album);
  Vue.set(full_data,'viewmode',1);
  $('#gallery').removeClass('hidden');
  gallery_scroll_reset();
  resize_gallery();
  update_title();
}
function gallery_collapse() {
  Vue.set(full_data,'viewmode',0);
  $('#gallery').addClass('hidden');
  resize_gallery();
  update_title();
}

function resize_gallery() {
  var g = $('#gallery');
  if (g.hasClass('hidden'))
    g.height(0);
  else
    g.height(g.find('.detail').height() || get_gallery_photo_height());
}
function resize_updete() {
  gallery_photo_resized = true;
  $('.photo.cover.square').height($('.photo.cover.square').width());
  gallery_collapse();
}

function get_gallery_photo_y_offset() {
  var result = [];
  $('.gallery .photo').each(function(i,e){result.push($(e).offset().left)});
  return result;
}

var $scroller = $('.horizontal.scroller');
var scrolling = false;
function gallery_scroll(direction) {
  if (scrolling)
    return;

  var current = $scroller.scrollLeft();
  var offsets = get_gallery_photo_y_offset();

  var min_value;
  var min_index = 0;
  for (var i = 0; i < offsets.length; i++) {
    var value = Math.abs(offsets[i]);
    if (min_value === undefined || min_value > value){
      min_index = i;
      min_value = value;
    }
  }

  var target_index = min_index + direction;
  var target = offsets[target_index] + current;
  var distance = Math.abs(offsets[target_index]);

  if (target_index < 0 || target_index >= offsets.length)
    return;

  scrolling = true;
  $scroller.animate({
     scrollLeft: target,
  }, distance / 2, function() {
    // Animation complete.
    scrolling = false;
  });
}
function gallery_scroll_reset() {
  scrolling = true;
  $scroller.animate({
     scrollLeft: 0,
  }, $scroller.scrollLeft() / 2, function() {
    // Animation complete.
    scrolling = false;
  });
}
function horizontal_scroll(e) {
  if (scrolling) {
    e.preventDefault();
    return;
  }
  e = window.event || e;
  var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));
  if (delta == 0)
    return;
  else if (delta < 0)
  {
    if ($scroller.scrollLeft() >= ($scroller[0].scrollWidth - $scroller.width()))
      return
    direction = 1;
  }
  else
  {
    if ($scroller.scrollLeft() <= 0)
      return;
    direction = -1;
  }

  gallery_scroll(direction);
  e.preventDefault();
}
$scroller.bind('mousewheel DOMMouseScroll',horizontal_scroll);
$(window).resize(resize_updete);
$(resize_updete);
