import urllib2


def http_response_ok(url):
    try:
        r = urllib2.urlopen(url)
    except urllib2.URLError:
        return False
    if r.code == 200:
        return True
    else:
        return False
