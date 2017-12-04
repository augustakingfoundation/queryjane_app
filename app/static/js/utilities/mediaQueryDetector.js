// Inspired on the following technique http://stackoverflow.com/a/28373319
!function(global) {
  'use strict';

  var previousMediaQueryDetector = global.MediaQueryDetector;

  function MediaQueryDetector(options) {
    var options = options || {};
    var $target;

    function init() {
      $target = options.$target;
    }

    // Evaluate one or multiple breakpoints (params: xs, sm, md, lg)
    function isDevice() {
      var visibleElement;

      visibleElement = $target.find(':visible').attr('class');

      for (var i in arguments) {
        if(('visible-' + arguments[i]) == visibleElement) {
          return true;
        }
      }
    }

    init();

    return {
      isDevice: isDevice
    }
  }

  MediaQueryDetector.noConflict = function noConflict() {
    global.MediaQueryDetector = previousMediaQueryDetector;
    return MediaQueryDetector;
  };

  global.MediaQueryDetector = MediaQueryDetector;
}(this);
