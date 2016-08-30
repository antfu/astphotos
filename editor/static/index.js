
Vue.directive('editable',{
  twoWay: true,
  bind: function(text) {
    var vmi = this;
    var el = $(this.el).empty();
    $('<span>').text(text).appendTo(el);
    $('<input>').val(text).hide().on('blur',function() {
      text = el.find('input').val();
      vmi.set(text)
      el.find('span').text(text);
      el.find('input').val(text);
      el.find('span').show();
      el.find('input').hide();
    }).appendTo(el);
    el.on('dblclick',function() {
      el.find('span').hide();
      el.find('input').show().focus();
    });
  },
  update: function(text) {
    var el = $(this.el);
    el.find('span').text(text);
    el.find('input').val(text);
  },
  unbind: function() {
    var el = $(this.el);
    el.text('ADD');
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
    }
  }
});


$(function() {
  vm.update();
})
