;(function (Vue, options) {
  var emphasis = [
    'flash',
    'shake',
    'pulse',
    'tada',
    'bounce'
  ];

  var appearance = [
    'slide up',
    'slide down',
    'vertical flip',
    'horizontal flip',
    'fade',
    'fade up',
    'fade down',
    'fade left',
    'fade right',
    'scale',
    'drop',
    'browse'
  ];

  var defineEmphasis = function (name, duration) {
    return {
      beforeEnter: function (el) {
        $(el).show();
      },
      enter: function (el, done) {
        $(el).transition(name, duration, done);
        return function() {
          $(el).transition('stop');
        }
      },
      leave: function (el, done) {
        $(el)
          .transition('reset')
          .transition(name, duration, done)
          .hide();
        return function() {
            $(el).transition('stop');
        }
      }
    };
  };
  var defineAppearance = function (name, duration) {
    return {
      enter: function (el, done) {
        $(el)
          .transition('reset')
          .transition(name + ' in', duration, done);
        return function() {
          $(el).transition('stop');
        }
      },

      leave: function (el, done) {
        $(el)
          .transition('reset')
          .transition(name + ' out', duration, done);
        return function() {
          $(el).transition('stop');
        }
      }
    };
  };

  //Register all transitions globally
  var duration = (options || {}).duration || 700;

  emphasis.forEach(function (animation) {
    var definition = defineEmphasis(animation, duration);
    Vue.transition(animation, definition);
  });
  appearance.forEach(function (animation) {
    var definition = defineAppearance(animation, duration);
    var id = animation.split(' ').join('-');
    Vue.transition(id, definition);
  });
})(Vue)
