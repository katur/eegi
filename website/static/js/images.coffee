$(document).ready ->
  initializeRotatingImages()


initializeRotatingImages = ->
  rotators = $(".rotating-images")
  return if !rotators.length

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
