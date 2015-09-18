from decimal import Decimal

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


@register.simple_tag
def url_replace(request, field, value):
    query_dict = request.GET.copy()
    query_dict[field] = value
    return query_dict.urlencode()


@register.filter(is_safe=True)
def concatenate_ids_with_commas(l):
    s = ''
    for item in l:
        s += str(item.id) + ','
    if len(s) > 0:
        s = s[:-1]

    return s


@register.filter(is_safe=True)
def get_celsius_string(temperature):
    if temperature:
        return unicode(temperature) + u'\xb0' + 'C'
    else:
        return None


@register.simple_tag
def get_screen_type(temperature, strain):
    category = strain.get_screen_category(temperature)
    if category == 'SUP':
        return 'SUP screen temperature'
    elif category == 'ENH':
        return 'ENH screen temperature'
    else:
        return 'neither SUP nor ENH screen temperature'


@register.simple_tag
def get_image_url(experiment, well, mode=None):
    """Get an image url."""
    if mode == 'thumbnail':
        image_url = experiment.get_thumbnail_url(well)
    elif mode == 'devstar':
        image_url = experiment.get_devstar_image_url(well)
    else:
        image_url = experiment.get_image_url(well)

    return image_url


@register.simple_tag
def get_score_summary(experiment, well):
    scores = experiment.get_scores(well)
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
