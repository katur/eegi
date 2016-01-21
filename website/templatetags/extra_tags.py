from django import template

from utils.well_tile_conversion import well_to_tile

register = template.Library()


@register.filter
def can_change_experiments(user):
    return user.has_perms(['experiments.change_experiment',
                           'experiments.change_experimentplate'])


@register.simple_tag
def url_replace(request, field, value):
    """
    Set GET[field] to value in the url.

    Keeps other GET key/value pairs intact.
    """
    query_dict = request.GET.copy()
    query_dict[field] = value
    return query_dict.urlencode()


@register.filter(is_safe=True)
def celsius(temperature):
    """Return temperature in format 22.5C, including degree sign."""
    if temperature:
        return u'{}{}C'.format(unicode(temperature), u'\N{DEGREE SIGN}')
    else:
        return None


@register.filter(is_safe=True)
def get_comma_separated_ids(l):
    """
    Get a comma-separated string of the IDs of the elements of l.

    Does not add spaces before or after the commas. This is because this
    is typically meant for non-pretty contexts (e.g. creating URLs).
    """
    return ','.join([str(item.id) for item in l])


@register.filter(is_safe=True)
def get_comma_separated_strings(l, add_links=False):
    """
    Get a comma-separated string of the items of l.

    For each item, favor get_display_string() if defined.
    Otherwise, uses the str() method.

    Optionally pass add_links=True to have each string be a link.
    URLs favor get_absolute_url() if defined. Otherwise, tries get_url().
    Otherwise, does '#'.

    Adds a space after the commas. This is because this function is meant
    for "pretty" contexts.
    """
    def get_string(item):
        try:
            return item.get_display_string()
        except AttributeError:
            return str(item)

    def get_url(item):
        try:
            return item.get_absolute_url()
        except AttributeError:
            return item.get_url()
        except AttributeError:
            return '#'

    if add_links:
        strings = ['<a href="{}">{}</a>'.format(
                   get_url(item), get_string(item)) for item in l]

    else:
        strings = [get_string(item) for item in l]

    return ', '.join(strings)


@register.filter
def get_comma_separated_targets(clone):
    """
    Get a comma-separated string of clone's targets.

    Adds a space after the commas.
    """
    genes = [x.gene for x in clone.get_targets()]
    if genes:
        return get_comma_separated_strings(genes, add_links=True)
    else:
        return "None (according to Firoz's database)"


@register.filter
def get_id_with_plate_link(item):
    """
    Get HTML where text is item.id, and the plate portion of the id
    links to item.plate.get_absolute_url.

    Requires that item.id is in format 'plate_well', that item has attribute
    'plate', and that plate in turn has the function get_absolute_url().

    If any of the above conditions do not hold, returns str(item).
    """
    try:
        plate, well = item.id.split('_')
        url = item.plate.get_absolute_url()
        return '<a href="{}">{}</a>_{}'.format(url, plate, well)
    except Exception:
        return str(item)


@register.filter
def get_screen_type(worm, temperature):
    """Get string of the screen evidenced by this worm and temperature."""
    if worm.is_permissive_temperature(temperature):
        return 'ENH'
    elif worm.is_restrictive_temperature(temperature):
        return 'SUP'
    else:
        return ''


@register.simple_tag
def get_image_url(experiment, mode=None):
    """
    Get the url for an experiment's image.

    Set mode to 'thumbnail' or 'devstar' for either of those image
    types. Otherwise, returns the normal full-size image.
    """
    return experiment.get_image_url(mode=mode)


@register.filter
def get_tile(well):
    """Get the tile, e.g. Tile000094, corresponding to well."""
    return well_to_tile(well)


@register.filter
def get_manual_score_summary(experiment):
    """
    Get a string summarizing the scores for this experiment.

    Groups such that scores by different scorers, and scores made at
    different timepoints, can be distinguished.
    """
    scores = experiment.get_manual_scores()
    d = {}
    for score in scores:
        scorer = score.scorer
        timestamp = score.timestamp
        if scorer not in d:
            d[scorer] = {}
        if timestamp not in d[scorer]:
            d[scorer][timestamp] = []
        d[scorer][timestamp].append(score.score_code.short_description)

    people = []
    for s in d:
        output = '{}:'.format(s.get_short_name())
        for t in d[s]:
            t_string = t.strftime('%Y-%m-%d %H:%M')
            joined = ', '.join(str(item) for item in d[s][t])
            output += ' {} ({})'.format(joined, t_string)
        people.append(output)

    return '; '.join(str(item) for item in people)


@register.filter
def get_devstar_score_summary(experiment):
    """Get a string summarizing the DevStaR score for this experiment."""
    scores = experiment.get_devstar_scores()

    output = []

    for score in scores:
        o = '{} adults, {} larvae, {} embryos'.format(
            score.count_adult, score.count_larva, score.count_embryo)

        if isinstance(score.survival, float):
            o += ', {:.2f} survival'.format(score.survival)
        else:
            o += ', {} survival'.format(score.survival)

        if score.is_bacteria_present:
            o += ', bacteria detected'
        output.append(o)

    return '; '.join(str(item) for item in output)
