$(document).ready(function() {
  removePageTitleStyleIfEmpty();
  setResizeHandler();
  positionFooter();
  hover_tags();
  initializeModals();
});


ESCAPE_KEY = 27;


function initializeModals() {
  $("body").on("click", "[data-modal-id]", function(e) {
    e.preventDefault();
    var modalId = $(e.currentTarget).attr("data-modal-id");
    $("#" + modalId).addClass("visible");
  });

  $("body").on("click", ".modal-close", function(e) {
    e.preventDefault();
    $(".modal-wrapper").removeClass("visible");
  });

  $("body").on("click", ".modal-wrapper", function(e) {
    e.preventDefault();

    if ($(e.target).closest(".modal").length) {
      return;
    };

    $(".modal-wrapper").removeClass("visible");
  });

  $("body").on("keyup", function(e) {
    if (e.which == ESCAPE_KEY) {
      $(".modal-wrapper").removeClass("visible");
    }
  });
};


function removePageTitleStyleIfEmpty() {
  var pageTitle = $("#page-title");
  if (pageTitle.is(":empty")) {
    pageTitle.remove();
  }
};


function setResizeHandler() {
  $(window).resize(function() {
    positionFooter();
  });
};


function positionFooter() {
  var footer = $("#footer");
  var footerHeight = footer.outerHeight();
  var footerWidth = footer.width();
  var windowHeight = $(window).height();
  var contentHeight = $("html").height();

  if (footer.css("position") === "absolute") {
    contentHeight += footerHeight;
  }

  var cssDict;
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

  footer.css(cssDict);
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

    tag.css({
      top: position.top - tag.outerHeight(),
      left: position.left - tag.outerWidth() / 2 + target.width() / 2
    }).show();
  });

  $('body').on('mouseout', '[data-hover-tag]', function(e) {
    $('.hover_tag').hide();
  });
};
