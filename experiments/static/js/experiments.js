$(document).ready(function() {
  initializeCarousels();
  ScoringKeyboardShortcuts.init();
});


var ScoringKeyboardShortcuts = {
  DIRECTIONS: {
    UP: "UP",
    DOWN: "DOWN",
  },

  KEYS: {
    UP: 38,
    DOWN: 40,
  },

  isDigitKey: function(key) {
    return key >= 48 && key <= 57;
  },

  getDigitKey: function(key) {
    return key - 48;
  },

  init: function() {
    if (!$("#score-experiment-wells").length) {
      return;
    }

    this.experiments = $(".experiment");
    if (!this.experiments.length) {
      return;
    }

    this.currentExperimentIndex = 0;
    this.activateExperiment($(this.experiments[this.currentExperimentIndex]));
    this.listen();
  },

  listen: function() {
    $("body").on("keydown", function(e) {
      ScoringKeyboardShortcuts.handleKeyboardShortcut(e);
    });
  },

  handleKeyboardShortcut: function(e) {
    switch(e.which) {
      case this.KEYS.UP:
        e.preventDefault();
        this.navigate(this.DIRECTIONS.UP);
        break;

      case this.KEYS.DOWN:
        e.preventDefault();
        this.navigate(this.DIRECTIONS.DOWN);
        break;

      default:
        if (!this.isDigitKey(e.which)) {
          return;
        }

        this.score(this.getDigitKey(e.which));
    }
  },

  navigate: function(direction) {
    var nextExperimentIndex;
    if (direction === this.DIRECTIONS.UP) {
      nextExperimentIndex = this.currentExperimentIndex - 1;
    } else if (direction === this.DIRECTIONS.DOWN) {
      nextExperimentIndex = this.currentExperimentIndex + 1;
    }

    if (nextExperimentIndex < 0 ||
        nextExperimentIndex >= this.experiments.length) {
      return;
    }

    var nextExperiment = $(this.experiments[nextExperimentIndex]);
    this.scrollToExperiment(nextExperiment);
    this.currentExperimentIndex = nextExperimentIndex;
  },

  score: function(key) {
    var group = this.getKeyableGroup();
    var input = group.find(".keyable")[key];
    $(input).trigger("click");
    this.keyableGroupIndex += 1;
    this.activateKeyableGroup();
  },

  setKeyableGroups: function(experiment) {
    var buttons = experiment.find(".keyable");
    var groups = [];

    buttons.each(function() {
      var id = $(this).closest("ul").attr("id");

      if (id != groups[groups.length - 1]) {
        groups.push(id);
      }
    });

    this.keyableGroups = groups;
    this.keyableGroupIndex = 0;
  },

  scrollToExperiment: function(experiment) {
    this.activateExperiment(experiment);
    $("html, body").scrollTop(experiment.position().top);
  },

  activateExperiment: function(experiment) {
    $(this.experiments).removeClass("active");
    experiment.addClass("active");
    this.setKeyableGroups(experiment);
    this.activateKeyableGroup();
  },

  activateKeyableGroup: function() {
    $(".active-keyable-group").removeClass("active-keyable-group");
    var group = this.getKeyableGroup();
    group.addClass("active-keyable-group");
  },

  getKeyableGroup: function() {
    return $("#" + this.keyableGroups[this.keyableGroupIndex]);
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
