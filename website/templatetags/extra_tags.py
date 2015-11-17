from django import template

from utils.well_tile_conversion import well_to_tile

register = template.Library()


@register.filter
def get_range(value):
    return range(value)


@register.simple_tag
def url_replace(request, field, value):
    """Set GET[field] to value in the url.

    Keeps other GET key/value pairs intact.
    """
    query_dict = request.GET.copy()
    query_dict[field] = value
    return query_dict.urlencode()


@register.filter(is_safe=True)
def concatenate_ids_with_commas(l):
    """Get a string that is elements of l, separated by commas.

    Does not add spaces before or after the commas.

    """
    return ','.join([str(item.id) for item in l])


@register.filter(is_safe=True)
def celsius(temperature):
    """Return temperature in format 22.5C, including degree sign."""
    if temperature:
        return unicode(temperature) + u'\N{DEGREE SIGN}' + 'C'
    else:
        return None


@register.filter
def get_screen_category(worm, temperature):
    """Get a string describing if temperature is an official screening
    temperature for worm strain.

    """
    if worm.is_permissive_temperature(temperature):
        return 'ENH'
    elif worm.is_restrictive_temperature(temperature):
        return 'SUP'
    else:
        return ''


@register.filter
def is_manually_scored(experiment):
    """Determine whether an experiment was manually scored."""
    return experiment.is_manually_scored()


@register.filter
def is_devstar_scored(experiment):
    """Determine whether an experiment was scored by DevStaR."""
    return experiment.is_devstar_scored()


@register.filter
def get_tile(well):
    return well_to_tile(well)


@register.filter
def get_manual_score_summary(experiment):
    """Get a string summarizing the scores for this experiment.

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
        output = s.get_short_name() + ': '
        for t in d[s]:
            t_string = t.strftime('%Y-%m-%d %H:%M')
            joined = ', '.join(str(item) for item in d[s][t])
            output += joined + ' (' + t_string + ')'
        people.append(output)

    return '; '.join(str(item) for item in people)


@register.filter
def get_devstar_score_summary(experiment):
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


@register.simple_tag
def get_worm_url(worm, request):
    return worm.get_url(request)


@register.simple_tag
def get_image_url(experiment, mode=None):
    """Get the url for an experiment's image.

    Set mode to 'thumbnail' or 'devstar' for either of those image
    types. Otherwise, returns the normal full-size image.

    """
    return experiment.get_image_url(mode=mode)


@register.filter
def list_targets(clone):
    targets = clone.get_targets()
    displays = [x.gene.get_display_string() for x in targets]
    if displays:
        return ', '.join(displays)
    else:
        return "None (according to Firoz's database)"
