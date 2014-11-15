$(document).ready ->
  removePageTitleStyleIfEmpty()
  setResizeHandler()
  positionFooter()
  initializeDoubleKnockdownPage()


initializeDoubleKnockdownPage = ->
  return if !$("body#double-knockdown").length

  rotatingImages = $(".rotating-images")

  rotatingImages.each ->
    el = $(this)
    el.find(".individual-image").first().addClass("show")

  rotatingImages.find(".experiment-image-wrapper").click ->
    showNextImage($(this).closest(".rotating-images"))


showNextImage = (rotatingImage) ->
  images = rotatingImage.find(".individual-image")
  i = images.index($(".show"))
  images.eq(i).removeClass("show")
  i = (++i) % images.length
  images.eq(i).addClass("show")


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
