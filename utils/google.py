"""Utility module for working with Google API."""

import gspread
import json
from oauth2client.client import SignedJwtAssertionCredentials

from django.conf import settings


def connect_to_google_spreadsheets():
    """Connect to Google Spreadsheets with API key."""
    json_key = json.load(open(settings.GOOGLE_API_KEY))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(
        json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    return gc
