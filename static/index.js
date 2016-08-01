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
  data: {
    title: "Astphoto",
    des: "A static photo gallery generator",
    album: undefined,
    current_page: 1
  },
  methods:
  {
    collapse: gallery_collapse
  }
});
var vue_inst_albums = new Vue({
  el: '#albums',
  data: {
    albums: [],
    gallery_view: false
  },
  methods: {
    expand: function (album) {
      if ($('#gallery').hasClass('hidden') || vue_inst_gallery.$data.photos != album.photos)
        gallery_expend(album);
      else
        gallery_collapse();
    }
  }
});
var vue_inst_gallery = new Vue({
  el: '#gallery',
  data: {
    photos: []
  },
  methods: {
    photo_height: get_gallery_photo_height
  }
});

$.getJSON('/static/struct.json',function(data){
  full_data = data;
  vue_inst_nav.$data.title = data.title;
  vue_inst_nav.$data.des = data.des;
  vue_inst_albums.$data.albums = data.albums;
})

function get_gallery_photo_height() {
  if (!gallery_photo_resized)
    return gallery_photo_height;
  var temp = $('<div class="gallery" class="opacity:0"><div class="photo"></div></div>').appendTo('body');
  gallery_photo_height = temp.find('.photo').height();
  gallery_photo_resized = false;
  temp.remove();
  return gallery_photo_height;
}

function gallery_expend(album) {
  vue_inst_gallery.$data = album;
  vue_inst_nav.$data.album = album;
  vue_inst_albums.$data.gallery_view = true;
  $('#gallery').removeClass('hidden');
  resize_gallery();
}
function gallery_collapse() {
  vue_inst_nav.$data.album_name = undefined;
  vue_inst_nav.$data.album = undefined;
  vue_inst_albums.$data.gallery_view = false;
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
  vue_inst_gallery.$data = {};
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
