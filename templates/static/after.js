'use strict';


/* =============== Vue Directive ===============*/
Vue.transition('height-toggle', {
  css: false,
  enter: function (el, done) {
    $(el).slideToggle('slow', done);
  },
  enterCancelled: function (el) {
    $(el).stop()
  },
  leave: function (el, done) {
    $(el).slideToggle('fast', done);
  },
  leaveCancelled: function (el) {
    $(el).stop()
  }
});

Vue.directive('background-photo',{
  update: function(url) {
    var el = $(this.el);
    var loader = el.parents().find('.loader').removeClass('hidden');
    el.css('transition','opacity 0.5s ease-in').css('opacity',0);
    var img = $('<img>', {
      src: url
    }).hide().on('load',function() {
      $(this).remove();
      el.css('background-image', 'url("'+url+'")').css('opacity',1);
      loader.addClass('hidden');
    }).appendTo(el);
  }
});
Vue.directive('photo',{
  update: function(url) {
    var el = $(this.el);
    var loader = el.parents().find('.loader').removeClass('hidden');
    el.attr('src',url);
    el.css('transition','opacity 0.5s ease-in').css('opacity',0);
    el.on('load', function(){
      el.css('opacity',1);
      loader.addClass('hidden');
    });
  }
});

/* =============== Vue Instance ===============*/
var vue_mix = vue_mix || {}
var vue_instance = new Vue({
  el: '#root',
  data: full_data,
  mixins: [vue_mix],
  methods: {
    // GALLERY
    gallery_expand: function(album) {
      if (this.$data.viewmode == 0 || this.$data.current != album)
      {
        Vue.set(this.$data,'current',album);
        Vue.set(this.$data.current,'page',1);
        Vue.set(this.$data,'viewmode',1);
        this.update_title();
        if (on_gallery_expand)
          on_gallery_expand.apply(this,album);
      } else {
        this.gallery_collapse();
      }
    },
    gallery_collapse: function() {
      Vue.set(this.$data,'viewmode',0);
      this.update_title();
      if (on_gallery_collapse)
        on_gallery_collapse.apply(this);
    },

    // MODAL
    modal_open: function(photo) {
      var vm = this;
      $.each(this.$data.current.photos,function (i,e) {
        if (e == photo)
        {
          Vue.set(vm.$data.current,'modal',i);
          Vue.set(vm.$data,'viewmode',2);
        }
      })
    },
    modal_close: function() {
      Vue.set(this.$data,'viewmode',1);
    },
    modal_next: function(direction) {
      var target = this.$data.current.modal + direction;
      if (target >= 0 && target < this.$data.current.amount)
        Vue.set(this.$data.current,'modal',target);
    },

    // COMONS
    dateformat: function(datestr) {
      var monthNames = [
        "January", "February", "March",
        "April", "May", "June", "July",
        "August", "September", "October",
        "November", "December"
      ];
      var date = new Date(datestr);
      var day = date.getDate();
      var monthIndex = date.getMonth();
      var year = date.getFullYear();
      return monthNames[monthIndex] + ' ' + year;
    },
    update_title: function() {
      if (!this.$data.viewmode)
        document.title = this.$data.title;
      else if (this.$data.current)
        document.title = this.$data.current.name + ' - ' + this.$data.title;
      else
        document.title = this.$data.title;
    }
  }
});

$(function(){
  vue_instance.update_title();
})
