$(document).ready(function() {
  initializeCarousels();
  ScoringKeyboardShortcuts.init();
});


var ScoringKeyboardShortcuts = {
  KEY_ORDER: "0123456789-QWERTY",

  DIRECTIONS: {
    UP: 38,
    DOWN: 40,
  },

  CODE_TO_SYMBOL: {
    189: "-",
  },

  getKeyFromCode: function(code) {
    if (this.isDigitKey(code)) {
      return this.getDigitKey(code);
    } else if (this.isAlphaKey(code)) {
      return this.getAlphaKey(code);
    } else {
      // Will return undefined if code is absent from dictionary
      return this.CODE_TO_SYMBOL[code];
    }
  },

  isDigitKey: function(code) {
    return code >= 48 && code <= 57;
  },

  getDigitKey: function(code) {
    return code - 48;
  },

  isAlphaKey: function(code) {
    return code >= 65 && code <= 90;
  },

  getAlphaKey: function(code) {
    return String.fromCharCode(code);
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
    this.activateExperiment();
    this.listen();
  },

  listen: function() {
    $("body").on("keydown", function(e) {
      ScoringKeyboardShortcuts.handleKeyboardShortcut(e);
    });
  },

  handleKeyboardShortcut: function(e) {
    switch(e.which) {
      case this.DIRECTIONS.UP:
        e.preventDefault();

        if (e.shiftKey) {
          this.navigateKeyableGroups(this.DIRECTIONS.UP);
        } else {
          this.navigateExperiments(this.DIRECTIONS.UP);
        }

        break;

      case this.DIRECTIONS.DOWN:
        e.preventDefault();

        if (e.shiftKey) {
          this.navigateKeyableGroups(this.DIRECTIONS.DOWN);
        } else {
          this.navigateExperiments(this.DIRECTIONS.DOWN);
        }

        break;

      default:
        var key = this.getKeyFromCode(e.which);
        var keyIndex = this.KEY_ORDER.indexOf(key);
        if (keyIndex >= 0) {
          this.score(keyIndex);
        }
    }
  },

  score: function(keyIndex) {
    var group = this.getKeyableGroup();
    var input = $(group.find(".keyable")[keyIndex]);

    // Do not proceed if keyIndex greater than number of keys
    if (!input.length) {
      return;
    }
    input.trigger("click");
    this.navigateKeyableGroups(this.DIRECTIONS.DOWN);
  },

  navigateExperiments: function(direction) {
    var nextIndex;
    if (direction === this.DIRECTIONS.UP) {
      nextIndex = this.currentExperimentIndex - 1;
    } else if (direction === this.DIRECTIONS.DOWN) {
      nextIndex = this.currentExperimentIndex + 1;
    }

    if (nextIndex < 0 || nextIndex >= this.experiments.length) {
      return;
    }

    this.currentExperimentIndex = nextIndex;
    this.activateExperiment();
  },

  navigateKeyableGroups: function(direction) {
    var nextIndex;
    if (direction === this.DIRECTIONS.UP) {
      nextIndex = this.keyableGroupIndex - 1;
    } else if (direction === this.DIRECTIONS.DOWN) {
      nextIndex = this.keyableGroupIndex + 1;
    }

    if (nextIndex < 0 || nextIndex >= this.keyableGroups.length) {
      return;
    }

    this.keyableGroupIndex = nextIndex;
    this.activateKeyableGroup();
  },

  activateExperiment: function() {
    $(this.experiments).removeClass("active");
    var experiment = $(this.experiments[this.currentExperimentIndex]);
    experiment.addClass("active");
    this.initializeKeyableGroups(experiment);
    this.activateKeyableGroup();
    $("html, body").scrollTop(experiment.position().top);
  },

  activateKeyableGroup: function() {
    $(".active-keyable-group").removeClass("active-keyable-group");
    var group = this.getKeyableGroup();
    group.addClass("active-keyable-group");
  },

  initializeKeyableGroups: function(experiment) {
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
