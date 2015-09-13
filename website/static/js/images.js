(function() {
  var addImageElement, initializeRotatingImages, showSubsequentImage;

  $(document).ready(function() {
    return initializeRotatingImages();
  });

  initializeRotatingImages = function() {
    var rotators;
    rotators = $(".rotating-images");
    if (!rotators.length) {
      return;
    }
    rotators.each(function() {
      var el, firstImage;
      el = $(this);
      firstImage = el.find(".individual-image").first();
      addImageElement(firstImage);
      return firstImage.addClass("show");
    });
    return rotators.find(".image-frame-navigation").click(function(e) {
      var direction, navigator, rotator;
      e.preventDefault();
      navigator = $(this);
      rotator = navigator.closest(".rotating-images");
      if (navigator.hasClass("image-frame-previous")) {
        direction = "previous";
      } else {
        direction = "next";
      }
      return showSubsequentImage(rotator, direction);
    });
  };

  showSubsequentImage = function(rotator, direction) {
    var currentImage, i, images, subsequentImage;
    images = rotator.find(".individual-image");
    currentImage = rotator.find(".show");
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
