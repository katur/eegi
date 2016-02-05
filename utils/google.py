"""Utility module for working with Google API."""

import gspread
import json
from oauth2client.client import SignedJwtAssertionCredentials

from eegi.settings import GOOGLE_API_KEY


def connect_to_google_spreadsheets():
    """Connect to Google Spreadsheets with API key."""
    json_key = json.load(open(GOOGLE_API_KEY))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(
        json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    return gc
