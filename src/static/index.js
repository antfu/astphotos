Vue.config.debug = true;
Vue.config.delimiters = ['${', '}'];
var full_data = {};

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
Vue.directive('horizontal-scrollable-photo',{
  bind:function(){
    var pic = $(this.el);
    pic.bind('mousewheel DOMMouseScroll',scroll.scrollwheel);
  }
});
Vue.directive('modal-image', function (id) {
  var pic = $(this.el).removeClass('horizontal vertical');
  var modal_data = full_data.current.photos[id];
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
    photo_height: get_gallery_photo_height,
    open_modal: function (photo) {
      $.each(full_data.current.photos,function (i,e) {
        if (e == photo)
        {
          Vue.set(full_data.current,'modal',i);
          Vue.set(full_data,'viewmode',2);
        }
      })
    }
  }
});
var vue_inst_modal = new Vue({
  el: '#modal',
  data: full_data,
  methods: {
    close: function () {
      Vue.set(full_data,'viewmode',1);
    },
    next: function (direction) {
      var target = full_data.current.modal + direction;
      if (target >= 0 && target < full_data.current.amount)
        Vue.set(full_data.current,'modal',target);
    }
  }
});

$.getJSON('/static/struct.json',function(data){
  full_data = data;
  vue_inst_nav.$data = full_data;
  vue_inst_albums.$data = full_data;
  vue_inst_gallery.$data = full_data;
  vue_inst_modal.$data = full_data;
  update_title();
  resize_gallery();
})

function update_title() {
  if (full_data.viewmode == 0)
    document.title = full_data.title;
  else if (full_data.current) {
    document.title = full_data.current.name + ' - ' +full_data.title;
  }
}

var gallery_photo_resized = true;
var gallery_photo_height = 0;
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
  Vue.set(full_data.current,'page',1);
  Vue.set(full_data,'viewmode',1);
  $('#gallery').removeClass('hidden');
  scroll.reset();
  // Reset body scrollTop
  $('body').animate({
     scrollTop: 0,
  }, $('body').scrollTop(), function() {});
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

function resize_update() {
  gallery_photo_resized = true;
  $('.photo.cover.square').height($('.photo.cover.square').width());
  gallery_collapse();
}

var $scroller = $('.horizontal.scroller');
var scroll = {
  scrolling: false,
  current: $scroller.scrollLeft,
  offsets: function () {
    var result = [];
    $('.gallery .photo').each(function(i,e){result.push($(e).offset().left)});
    return result;
  },
  scroll: function (direction) {
    if (scroll.scrolling)
      return;
    var offsets = scroll.offsets();
    var target_index = scroll.nesrest() + direction;
    if (target_index < 0 || target_index >= offsets.length)
      return;

    scroll.to(target_index);
  },
  to: function (index) {
    var offsets = scroll.offsets();
    if (index < 0 || index >= offsets.length)
      return;

    var target = offsets[index] + $scroller.scrollLeft();
    var distance = Math.abs(offsets[index]);

    scroll.scrolling = true;
    $scroller.animate({
      scrollLeft: target,
    }, distance / 2, function() {
      scroll.scrolling = false;
    });
  },
  reset: function () {
    scroll.scrolling = true;
    $scroller.animate({
       scrollLeft: 0,
    }, $scroller.scrollLeft() / 2, function() {
      // Animation complete.
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
    scroll.scroll(direction);
    e.preventDefault();
  }
}

$scroller.scroll(scroll.update);
$(window).resize(resize_update);
// Disable contextmenu
$('body').contextmenu(function(e) {
  e.preventDefault();
});
$(resize_update);
setTimeout(resize_update,500);
