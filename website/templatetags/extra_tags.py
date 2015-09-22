from django import template

register = template.Library()


@register.filter
def get_value(dictionary, key):
    """Get a dictionary value the normal way.

    Raises a KeyError if key is not present. So only use this when
    key being absent signifies a bug.

    """
    return dictionary[key]


@register.filter
def get_value_or_none(dictionary, key):
    """Get a dictionary value the safe way.

    Returns None if the key is not present.

    """
    return dictionary.get(key)


@register.filter
def is_key_present(dictionary, key):
    """Determine if a key is present in dictionary."""
    if dictionary.get(key):
        return True
    else:
        return False


@register.filter
def get_range(value):
    return range(value)


@register.filter(is_safe=True)
def concatenate_ids_with_commas(l):
    """Get a string that is elements of l, separated by commas.

    Does not add spaces before or after the commas.

    """
    s = ''
    for item in l:
        s += str(item.id) + ','
    if len(s) > 0:
        s = s[:-1]

    return s


@register.filter(is_safe=True)
def celsius(temperature):
    """Return temperature in format 22.5C, including degree sign."""
    if temperature:
        return unicode(temperature) + u'\xb0' + 'C'
    else:
        return None


@register.filter
def get_screen_type(strain, temperature):
    """Get a string describing if temperature is an official screening
    temperature for strain.

    """
    if strain.is_permissive_temperature(temperature):
        return 'ENH screen temperature'
    elif strain.is_restrictive_temperature(temperature):
        return 'SUP screen temperature'
    else:
        return 'neither SUP nor ENH screen temperature'


@register.simple_tag
def get_manual_score_summary(experiment, well):
    """Get a string summarizing the scores for this experiment.

    Groups such that scores by different scorers, and scores made at
    different timepoints, can be distinguished.

    """
    scores = experiment.get_manual_scores(well)
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


@register.simple_tag
def get_devstar_score_summary(experiment, well):
    scores = experiment.get_devstar_scores(well)

    output = []

    for score in scores:
        o = '{} adults, {} larvae, {} embryos, {:.2f} survival'.format(
            score.count_adult, score.count_larva, score.count_embryo,
            score.survival)
        if score.is_bacteria_present:
            o += ', bacteria detected'
        output.append(o)

    return '; '.join(str(item) for item in output)


@register.assignment_tag
def is_manually_scored(experiment, well):
    """Determine whether an experiment well was manually scored."""
    return experiment.is_manually_scored(well)


@register.assignment_tag
def is_devstar_scored(experiment, well):
    """Determine whether an experiment well was scored by DevStaR."""
    return experiment.is_devstar_scored(well)


@register.simple_tag
def url_replace(request, field, value):
    """Set GET[field] to value in the url.

    Keeps other GET key/value pairs intact.
    """
    query_dict = request.GET.copy()
    query_dict[field] = value
    return query_dict.urlencode()


@register.simple_tag
def get_image_url(experiment, well, mode=None):
    """Get the url for an image.

    Set mode to 'thumbnail' or 'devstar' for either of those image
    types. Otherwise, returns the normal full-size image.

    """
    if mode == 'thumbnail':
        image_url = experiment.get_thumbnail_url(well)
    elif mode == 'devstar':
        image_url = experiment.get_devstar_image_url(well)
    else:
        image_url = experiment.get_image_url(well)

    return image_url
