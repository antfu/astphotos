'use strict';

if (full_data)
  $('#warning').remove();

Vue.config.debug = DEBUG;
Vue.config.delimiters = ['${', '}'];

var vue_mix = vue_mix || {}
var vue_instance = new Vue({
  el: '#root',
  data: full_data,
  mixins: [vue_mix]
});
