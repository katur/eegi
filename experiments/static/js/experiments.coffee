$(document).ready ->
  initializeCarousels()


initializeCarousels = ->
  carousels = $(".carousel")
  return if !carousels.length

  carousels.each ->
    el = $(this)
    firstImage = el.find(".individual-image").first()
    addImageElement(firstImage)
    firstImage.addClass("show")

  carousels.find(".image-frame-navigation").click (e) ->
    e.preventDefault()
    navigator = $(this)
    carousel = navigator.closest(".carousel")

    if navigator.hasClass("image-frame-previous")
      direction = "previous"
    else
      direction = "next"

    showSubsequentImage(carousel, direction)


showSubsequentImage = (carousel, direction) ->
  images = carousel.find(".individual-image")
  currentImage = carousel.find(".show")
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
