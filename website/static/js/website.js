(function() {
  var positionFooter, removePageTitleStyleIfEmpty, setResizeHandler;

  $(document).ready(function() {
    removePageTitleStyleIfEmpty();
    setResizeHandler();
    return positionFooter();
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

}).call(this);
