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
})

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
  resize_gallery();
}
function gallery_collapse() {
  Vue.set(full_data,'viewmode',0);
  $('#gallery').addClass('hidden');
  resize_gallery();
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

function horizontal_scroll(e) {
  e = window.event || e;
  var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));
  var $scroller = $('.horizontal.scroller');
  var scroller = $scroller[0];
  scroller.scrollLeft -= (delta*40); // Multiplied by 40
  /*
  if (delta < 0) delta = -1;
  else if (delta == 0) delta = 0;
  else delta = 1;
  $('.horizontal.scroller')[0].scrollLeft -= (delta * $('#gallery .photo').width());
  */
  if (scroller.scrollLeft > 10 && scroller.scrollLeft < scroller.scrollWidth - $scroller.width() - 10)
    e.preventDefault();
}
$('.horizontal.scroller').bind('mousewheel DOMMouseScroll',horizontal_scroll);
$(window).resize(resize_updete);
$(resize_updete);
