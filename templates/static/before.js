'use strict';

if (full_data)
  $('#warning').remove();

/* =============== Data Process ===============*/
$.each(full_data.albums,function(_,album){
  var album_href_path = album.href_path;
  $.each(album.photos,function(_,photo){
    photo.path = album_href_path + '/' + photo.path;
  });
  album.cover = album_href_path + '/' + album.cover;
});
full_data.router = (window.location.hash || 'overview').replace('#','').split('|');

/* =============== Vue Config ===============*/
Vue.config.debug = DEBUG;
Vue.config.delimiters = ['${', '}'];

/* =============== Events ===============*/
var on_gallery_expand;
var on_gallery_collapse;
