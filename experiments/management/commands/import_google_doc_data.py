import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

from django.core.management.base import BaseCommand, CommandError

from eegi.settings import GOOGLE_API_KEY
from utils.scripting import require_db_write_acknowledgement


class Command(BaseCommand):
    help = 'Import the experiments recorded in Google Doc'

    def handle(self, **options):
        require_db_write_acknowledgement()

        json_key = json.load(open(GOOGLE_API_KEY))
        scope = ['https://spreadsheets.google.com/feeds']

        credentials = SignedJwtAssertionCredentials(
                json_key['client_email'], json_key['private_key'].encode(),
                scope)

        gc = gspread.authorize(credentials)
        sheet = gc.open('eegi_batch_experiment_entry').sheet1
        print sheet.cell(1, 3)

        print 'success'
