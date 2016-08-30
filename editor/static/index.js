function set_text($el,text) {
  if (text)
    return $el.removeClass('not-set').text(text);
  else
    return $el.addClass('not-set').text('not set');
}

Vue.directive('editable',{
  twoWay: true,
  bind: function(text) {
    text = text || '';
    var vmi = this;
    var el = $(this.el).empty();
    var span = $('<span>').appendTo(el);
    var input = $('<input>').val(text).hide().appendTo(el);

    function submit() {
      text = input.val();
      vmi.set(text)
      set_text(span,text).show();
      input.val(text).hide();
    }

    set_text(span,text);
    input.on('blur', submit);
    input.on('keypress', function (e) {
      // Enter pressed
      if(e.which === 13)
        submit();
    });
    el.on('dblclick',function() {
      span.hide();
      input.show().focus();
    });
  },
  update: function(text) {
    text = text || '';
    var el = $(this.el);
    set_text(el.find('span'),text);
    el.find('input').val(text);
  },
  unbind: function() {
    var el = $(this.el);
    el.empty();
  },
});

var vm = new Vue({
  el: '#root',
  data: {},
  methods: {
    update: function() {
      $.getJSON('/data',function(data) {
        vm.$data=data;
        console.log('Update',data);
      })
    },
    set_current: function(album) {
      Vue.set(vm.$data, 'current', album);
    },
    img_path: function(path) {
      return path.replace(/\\/g, '/');
    }
  }
});


$(function() {
  vm.update();
})
