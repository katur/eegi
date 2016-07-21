$(document).ready(function() {
  initializeCarousels();
  ScoringKeyboardShortcuts.init();
});


const DIRECTIONS = {
  UP: "UP",
  DOWN: "DOWN",
}


const KEYS = {
  UP: 38,
  DOWN: 40,
}


var ScoringKeyboardShortcuts = {
  init: function() {
    if (!$("#score-experiment-wells").length) {
      return;
    }

    this.experiments = $(".experiment");
    if (!this.experiments.length) {
      return;
    }

    this.currentIndex = 0;
    this.styleActiveExperiment($(this.experiments[this.currentIndex]));
    this.listen();
  },

  listen: function() {
    $("body").on("keydown", function(e) {
      ScoringKeyboardShortcuts.handleKeyboardShortcut(e);
    });
  },

  handleKeyboardShortcut: function(e) {
    switch(e.which) {
      case KEYS.UP:
        e.preventDefault();
        this.navigate(DIRECTIONS.UP);
        break;
      case KEYS.DOWN:
        e.preventDefault();
        this.navigate(DIRECTIONS.DOWN);
        break;
      default:
        if (!this.isDigit(e.which)) {
          return;
        }
        console.log("Digit " + this.getDigit(e.which));
    }
  },

  navigate: function(direction) {
    var nextIndex;
    if (direction === DIRECTIONS.UP) {
      nextIndex = this.currentIndex - 1;
    } else if (direction === DIRECTIONS.DOWN) {
      nextIndex = this.currentIndex + 1;
    }

    if (nextIndex < 0 || nextIndex >= this.experiments.length) {
      return;
    }

    var nextExperiment = $(this.experiments[nextIndex]);
    this.scrollToExperiment(nextExperiment);
    this.currentIndex = nextIndex;
  },

  scrollToExperiment: function(experiment) {
    this.styleActiveExperiment(experiment);
    $("html, body").scrollTop(experiment.position().top);
  },

  styleActiveExperiment: function(experiment) {
    $(this.experiments).removeClass("active");
    experiment.addClass("active");
  },

  isDigit: function(key) {
    return key >= 48 && key <= 57;
  },

  // Digit keys are 48 + digit
  getDigit: function(key) {
    return key - 48;
  },

};


function initializeCarousels() {
  var carousels = $(".carousel");
  if (!carousels.length) {
    return;
  }

  carousels.each(function() {
    var el = $(this);
    var firstImage = el.find(".individual-image").first();
    addImageElement(firstImage);
    firstImage.addClass("show");
  });

  carousels.find(".image-frame-navigation").click(function(e) {
    e.preventDefault();
    var navigator = $(this);
    var carousel = navigator.closest(".carousel");

    var direction;
    if (navigator.hasClass("image-frame-previous")) {
      direction = "previous";
    } else {
      direction = "next";
    }

    showSubsequentImage(carousel, direction);
  });
};


function showSubsequentImage(carousel, direction) {
  var images = carousel.find(".individual-image");
  var currentImage = carousel.find(".show");
  var i = images.index(currentImage);
  images.eq(i).removeClass("show");

  if (direction === "next") {
    i = (++i) % images.length;
  } else {
    i = (--i) % images.length;
  }

  var subsequentImage = images.eq(i);
  subsequentImage.addClass("show");
  addImageElement(subsequentImage);
};


function addImageElement(image) {
  var imageFrame = image.find(".image-frame");
  var imageSrc = imageFrame.attr("data-src");
  imageFrame.prepend("<img src='" + imageSrc + "' \>");
};
