$(document).ready ->
  removePageTitleStyleIfEmpty()
  setResizeHandler()
  positionFooter()
  hover_tags()


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


# FROM
# https://github.com/mgeraci/Coffee-Filter/blob/master/coffee_filter.coffee

# show a tag on hover (e.g., a username when hovering over an avatar)
# add the desired text as a data attribute on the element, e.g.:
#   <img src='/images/avatar.png' data-hover-tag='michael geraci'>
# optionally, add data-hover-tag-top and/or data-hover-tag-left
# to override the default offset
window.hover_tags = ->
  # position and show the tag on mouseover of element
  $('body').on 'mouseover', '[data-hover-tag]', (e)->
    target = $(this).closest('[data-hover-tag]')

    # Clean out hover tag title so browser hover doesn't show
    old_title = target.attr('title')
    target.attr('title', '')
    name = unescape(target.data('hover-tag')) # unescape in case you use line breaks

    # use title attr if no hover-tag defined
    if name == ''
      name = old_title
      target.data('hover-tag', old_title)

    position = target.offset()

    # append tag and styles if it doesn't exist
    if $('.hover_tag').length == 0

      # add the html structure
      $('body').append "
        <div class='hover_tag'>
          <div class='text'></div>
          <div class='tag_pointer'></div>
        </div>"

    tag = $('.hover_tag')

    # set the text
    tag.find('.text').html(name)

    # position and show the tag
    tag.css(
      top: position.top - tag.outerHeight()
      left: position.left - tag.outerWidth() / 2 + target.width() / 2
    ).show()

  # hide the tag on mouseout of element
  $('body').on 'mouseout', '[data-hover-tag]', (e)->
    $('.hover_tag').hide()
