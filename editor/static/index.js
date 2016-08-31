function set_text($el,text) {
  if (text)
    return $el.removeClass('not-set').text(text);
  else
    return $el.addClass('not-set').text('not set');
}

function value_update(host, key, value) {
  var path;
  if (host && host._src_path)
    path = host._src_path;
  else
    path = 'img\\_site.json';

  console.log(path+'  -> '+key+' : "'+value+'"');

  $.ajax({
    type:"POST",
    url:'/api/json_update',
    data:JSON.stringify({path:path,key:key,value:value}),
    contentType: "application/json; charset=utf-8",
    dataType: "json"
  })
}


function FileSelectHandler(e) {
  console.log(e);
	// cancel event and hover styling
	FileDragHover(e);

	// fetch FileList object
	var files = e.target.files || e.originalEvent.dataTransfer.files;

	// process all File objects
	for (var i = 0, f; f = files[i]; i++) {
    console.log(f);
	}
  return false;
}
function FileDragHover(e) {
	e.stopPropagation();
	e.preventDefault();
	e.target.className = (e.type == "dragover" ? "hover" : "");
  return false;
}

if (window.File && window.FileList && window.FileReader) {
  var fileselect = $('#fileselect');
	var filedrag = $('#file_upload');
		//submitbutton = $id("submitbutton");

	// file select
	fileselect.on('change', FileSelectHandler);

	// is XHR2 available?
	var xhr = new XMLHttpRequest();
	if (xhr.upload) {
		// file drop
		filedrag.on("dragover", FileDragHover);
		filedrag.on("dragleave", FileDragHover);
		filedrag.on("drop", FileSelectHandler);
	}
}
else
{
  $('#file_upload').closest('.photo').remove();
}

Vue.directive('editable',{
  twoWay: true,
  bind: function(text) {
    var vmi = this;

    text = text || '';
    var el = $(vmi.el).empty();
    var span = $('<span>').appendTo(el);
    var input = $('<input>').val(text).hide().appendTo(el);

    function submit() {
      span.show();
      input.hide();

      var new_text = input.val();
      if ((new_text+'') === (text+''))
        return;
      text = new_text
      vmi.set(text);
      set_text(span,text);
      input.val(text);

      var expressions = vmi.expression.split('.');
      var scope = vmi._scope || vm;
      var host = scope;
      var key = expressions[expressions.length-1];
      for (var i=0; i<expressions.length-1; i++)
        host = host[expressions[i]];
      value_update(host, key, text);
    }
    function cancel() {
      set_text(span,text).show();
      input.val(text).hide();
    }

    set_text(span,text);
    input.on('blur', submit);
    input.on('keypress', function (e) {
      // Enter pressed
      if(e.which === 13)
        submit();
      // Escape pressed
      else if (e.which === 27)
        cancel();
    });
    el.on('click',function() {
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
  }
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
    },
    new_album: function() {

    }
  }
});

$(function() {
  vm.update();
})
