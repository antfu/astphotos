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

(function InitFileSelect() {
  function FileSelectHandler(e) {
  	FileDragHover(e);
  	var files = e.target.files || e.originalEvent.dataTransfer.files;
  	// process all File objects
  	for (var i = 0, f; f = files[i]; i++) {
      console.log(f);
      var filepath = vm.$data.current._src_path + '/' + f.name;
      $.ajax({
        type: 'post',
        url: '/upload?filename=' + filepath,
        data: f,
        success: function () {
          console.log('Uploaded ['+filepath+']');
        },
        xhrFields: {
          // add listener to XMLHTTPRequest object directly for progress (jquery doesn't have this yet)
          onprogress: function (progress) {
            // calculate upload progress
            var percentage = Math.floor((progress.total / progress.totalSize) * 100);
            // log upload progress to console
            console.log('progress', percentage);
            if (percentage === 100) {
              console.log('DONE!');
            }
          }
        },
        processData: false,
        contentType: f.type
      });
  	}
    $('#fileselect').val('');
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
  	fileselect.on('change', FileSelectHandler);
  	// is XHR2 available?
  	var xhr = new XMLHttpRequest();
  	if (xhr.upload) {
  		filedrag.on("dragover", FileDragHover);
  		filedrag.on("dragleave", FileDragHover);
  		filedrag.on("drop", FileSelectHandler);
  	}
  }
  else
  {
    $('#file_upload').closest('.photo').remove();
  }
})();

Vue.directive('editable',{
  twoWay: true,
  bind: function(text) {
    var vmi = this;
    var el = $(vmi.el).empty();

    vmi.text = text || '';
    vmi.span = $('<div>').addClass('text').appendTo(el);
    vmi.input = $('<input>').val(vmi.text).hide().appendTo(el);

    vmi.set_text = function()
    {
      if (vmi.text)
        return vmi.span.removeClass('not-set').text(vmi.text);
      else
        return vmi.span.addClass('not-set').text('not set');
    };
    vmi.submit = function() {
      vmi.escape();

      var new_text = vmi.input.val();
      if ((new_text+'') === (vmi.text+''))
        return;
      vmi.text = new_text;
      vmi.set_text();
      vmi.input.val(vmi.text);

      var expressions = vmi.expression.split('.');
      var scope = vmi._scope || vm;
      var host = scope;
      var key = expressions[expressions.length-1];
      for (var i=0; i<expressions.length-1; i++)
        host = host[expressions[i]];
      value_update(host, key, vmi.text);
    };
    vmi.cancel = function() {
      vmi.set_text();
      vmi.span.show();
      vmi.input.val(vmi.text).hide();
    };
    vmi.edit = function() {
      vmi.span.hide();
      vmi.input.show().focus();
    };
    vmi.escape = function() {
      vmi.span.show();
      vmi.input.hide();
    };

    vmi.set_text();
    vmi.input.on('blur', vmi.submit);
    vmi.input.on('keydown', function (e) {
      // Enter pressed
      if(e.which === 13)
        vmi.submit();
      // Escape pressed
      else if (e.which === 27)
        vmi.cancel();
    });
    el.on('click', vmi.edit);
  },
  update: function(text) {
    var vmi = this;
    vmi.text = text || '';
    vmi.set_text();
    vmi.input.val(vmi.text);
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
