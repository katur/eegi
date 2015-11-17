"""Utility module with helpers for HTTP response querying."""

import urllib2


def http_response_ok(url):
    """Return True if a url responds with "ok" HTTP status, False otherwise"""
    try:
        r = urllib2.urlopen(url)

    except urllib2.URLError:
        return False

    return r.code == 200
