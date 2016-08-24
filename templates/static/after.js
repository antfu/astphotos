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
  watch: {
    'router': function(val, oldVal) {
      console.log('router_changed', oldVal, val);
      this.router_parser(val, oldVal);
      window.location.hash = this.$data.router.join('|');
      if (on_router_changed)
        on_router_changed.apply(this,val);
    },
    'viewmode': function(val, oldVal) {
      this.update_title();
      if (val !== oldVal)
      {
        if (val === 0)
        {
          if (on_gallery_collapse)
            on_gallery_collapse.apply(this);
        }
        else if (val === 1)
        {
          if (on_gallery_expand)
            on_gallery_expand.apply(this, this.$data.current);
        }
      }
    }
  },
  methods: {
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
    },
    get_photographer_link: function(photographer_name)
    {
      return undefined;
    },

    find_album_by_name: function(album_name) {
      for (var i=0;i<this.$data.albums.length;i++)
        if (this.$data.albums[i].name == album_name)
          return this.$data.albums[i];
      return undefined;
    },

    go: function() {
      var args = [].slice.call(arguments);
      Vue.set(this.$data, 'router', args);
    },
    route: function() {
      var args = [].slice.call(arguments);
      for (var i=0; i<args.length; i++)
        if (this.$data.router[i] != args[i])
          return false;
      return true;
    },
    router_append: function(target, index) {
      index = index || 0;
      this.$data.router.splice(index);
      Vue.set(this.$data.router, index, target);
    },
    router_back: function(index) {
      index = index || (this.$data.router.length - 2) || 0;
      this.$data.router.splice(index);
    },
    router_parser: function(curr, old) {
      curr = curr || [];
      old  = old  || [];
      if (curr[0] === 'albums')
      {
        var album = this.find_album_by_name(curr[1]);
        if (album)
        {
          Vue.set(this.$data,'current', album);
          Vue.set(this.$data.current,'page', parseInt(curr[2] || 1));
          Vue.set(this.$data,'viewmode', 1);
        }
        else
          Vue.set(this.$data,'viewmode',0);
        return;
      }
      if (old[0] === 'albums' && curr[0] !== 'albums')
        Vue.set(this.$data,'viewmode',0);
    }
  }
});

$(function(){
  vue_instance.update_title();
  vue_instance.router_parser();
})
