"""Utility module with helpers for HTTP response querying."""

import urllib
import urllib2
from django.core.urlresolvers import reverse


def http_response_ok(url):
    """Return True if a url responds with "ok" HTTP status, False otherwise"""
    try:
        r = urllib2.urlopen(url)

    except urllib2.URLError:
        return False

    return r.code == 200


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.urlencode(get)
    return url
