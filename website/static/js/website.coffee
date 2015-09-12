$(document).ready ->
  removePageTitleStyleIfEmpty()
  setResizeHandler()
  positionFooter()
  initializeDoubleKnockdownPage()


initializeDoubleKnockdownPage = ->
  # return if !$("body#double-knockdown").length

  rotators = $(".rotating-images")

  rotators.each ->
    el = $(this)
    firstImage = el.find(".individual-image").first()
    addImageElement(firstImage)
    firstImage.addClass("show")

  rotators.find(".image-frame-navigation").click (e) ->
    e.preventDefault()
    navigator = $(this)
    rotator = navigator.closest(".rotating-images")

    if navigator.hasClass("image-frame-previous")
      direction = "previous"
    else
      direction = "next"

    showSubsequentImage(rotator, direction)


showSubsequentImage = (rotator, direction) ->
  images = rotator.find(".individual-image")
  currentImage = rotator.find(".show")
  i = images.index(currentImage)
  images.eq(i).removeClass("show")
  if direction == "next"
    i = (++i) % images.length
  else
    i = (--i) % images.length
  subsequentImage = images.eq(i)
  subsequentImage.addClass("show")
  addImageElement(subsequentImage)


addImageElement = (image) ->
  imageFrame = image.find(".image-frame")
  imageSrc = imageFrame.attr("data-src")
  imageFrame.prepend("<img src='#{imageSrc}' \>")


removePageTitleStyleIfEmpty = ->
  pageTitle = $("#page-title")
  if pageTitle.is(":empty")
    pageTitle.remove()


setResizeHandler = ->
  $(window).resize ->
    positionFooter()


positionFooter = ->
  footer = $("#footer")
  footerHeight = footer.outerHeight()
  footerWidth= footer.width()
  windowHeight = $(window).height()
  contentHeight = $("html").height()

  # if footer is absolute, it is not included in the content height, so add it
  if footer.css("position") == "absolute"
    contentHeight += footerHeight

  # if content is smaller than window, position the footer at bottom of page
  # otherwise position it statically (necessary in case user resizes window)
  if contentHeight < windowHeight
    cssDict =
      position: "absolute"
      bottom: parseInt($("body").css("paddingBottom"), 10)
      left: parseInt($("body").css("paddingLeft"), 10)
      width: footerWidth
  else
    cssDict =
      position: "static"

  footer.css(cssDict)
