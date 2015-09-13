"""Utility module with functionality to help with HTTP response querying."""

import urllib2


def http_response_ok(url):
    """Return True if a url responds with "ok" HTTP status, False otherwise"""
    try:
        r = urllib2.urlopen(url)
    except urllib2.URLError:
        return False
    if r.code == 200:
        return True
    else:
        return False
