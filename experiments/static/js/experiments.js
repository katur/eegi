(function() {
  var addImageElement, initializeCarousels, showSubsequentImage;

  $(document).ready(function() {
    return initializeCarousels();
  });

  initializeCarousels = function() {
    var carousels;
    carousels = $(".carousel");
    if (!carousels.length) {
      return;
    }
    carousels.each(function() {
      var el, firstImage;
      el = $(this);
      firstImage = el.find(".individual-image").first();
      addImageElement(firstImage);
      return firstImage.addClass("show");
    });
    return carousels.find(".image-frame-navigation").click(function(e) {
      var carousel, direction, navigator;
      e.preventDefault();
      navigator = $(this);
      carousel = navigator.closest(".carousel");
      if (navigator.hasClass("image-frame-previous")) {
        direction = "previous";
      } else {
        direction = "next";
      }
      return showSubsequentImage(carousel, direction);
    });
  };

  showSubsequentImage = function(carousel, direction) {
    var currentImage, i, images, subsequentImage;
    images = carousel.find(".individual-image");
    currentImage = carousel.find(".show");
    i = images.index(currentImage);
    images.eq(i).removeClass("show");
    if (direction === "next") {
      i = (++i) % images.length;
    } else {
      i = (--i) % images.length;
    }
    subsequentImage = images.eq(i);
    subsequentImage.addClass("show");
    return addImageElement(subsequentImage);
  };

  addImageElement = function(image) {
    var imageFrame, imageSrc;
    imageFrame = image.find(".image-frame");
    imageSrc = imageFrame.attr("data-src");
    return imageFrame.prepend("<img src='" + imageSrc + "' \>");
  };

}).call(this);
