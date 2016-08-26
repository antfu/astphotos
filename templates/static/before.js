'use strict';

if (full_data)
  $('#warning').remove();

/* =============== Data Process ===============*/
var overview_index = -1;
$.each(full_data.albums,function(i,album){
  var album_href_path = album.href_path;
  $.each(album.photos,function(_,photo){
    photo.path = album_href_path + '/' + photo.path;
  });
  album.cover = album_href_path + '/' + album.cover;
  if (album.name == '_overview')
  {
    full_data.overview_album = album;
    overview_index = i;
  }
});
if (overview_index != -1)
  full_data.albums.splice(overview_index,1);
full_data.router = (window.location.hash || 'overview').replace('#','').split('|');

/* =============== Vue Config ===============*/
Vue.config.debug = DEBUG;
Vue.config.delimiters = ['${', '}'];

/* =============== Events ===============*/
var on_gallery_expand;
var on_gallery_collapse;
var on_router_changed;
