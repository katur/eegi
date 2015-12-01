(function() {
  var positionFooter, removePageTitleStyleIfEmpty, setResizeHandler;

  $(document).ready(function() {
    removePageTitleStyleIfEmpty();
    setResizeHandler();
    positionFooter();
    return hover_tags();
  });

  removePageTitleStyleIfEmpty = function() {
    var pageTitle;
    pageTitle = $("#page-title");
    if (pageTitle.is(":empty")) {
      return pageTitle.remove();
    }
  };

  setResizeHandler = function() {
    return $(window).resize(function() {
      return positionFooter();
    });
  };

  positionFooter = function() {
    var contentHeight, cssDict, footer, footerHeight, footerWidth, windowHeight;
    footer = $("#footer");
    footerHeight = footer.outerHeight();
    footerWidth = footer.width();
    windowHeight = $(window).height();
    contentHeight = $("html").height();
    if (footer.css("position") === "absolute") {
      contentHeight += footerHeight;
    }
    if (contentHeight < windowHeight) {
      cssDict = {
        position: "absolute",
        bottom: parseInt($("body").css("paddingBottom"), 10),
        left: parseInt($("body").css("paddingLeft"), 10),
        width: footerWidth
      };
    } else {
      cssDict = {
        position: "static"
      };
    }
    return footer.css(cssDict);
  };

  window.hover_tags = function() {
    $('body').on('mouseover', '[data-hover-tag]', function(e) {
      var name, old_title, position, tag, target;
      target = $(this).closest('[data-hover-tag]');
      old_title = target.attr('title');
      target.attr('title', '');
      name = unescape(target.data('hover-tag'));
      if (name === '') {
        name = old_title;
        target.data('hover-tag', old_title);
      }
      position = target.offset();
      if ($('.hover_tag').length === 0) {
        $('body').append("<div class='hover_tag'> <div class='text'></div> <div class='tag_pointer'></div> </div>");
      }
      tag = $('.hover_tag');
      tag.find('.text').html(name);
      return tag.css({
        top: position.top - tag.outerHeight(),
        left: position.left - tag.outerWidth() / 2 + target.width() / 2
      }).show();
    });
    return $('body').on('mouseout', '[data-hover-tag]', function(e) {
      return $('.hover_tag').hide();
    });
  };

}).call(this);
