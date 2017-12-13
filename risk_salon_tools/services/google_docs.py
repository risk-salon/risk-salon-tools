import gspread

import pandas as pd

from oauth2client.service_account import ServiceAccountCredentials

from risk_salon_tools.services.config import Settings


class SheetsClient(object):
    scope = ['https://spreadsheets.google.com/feeds']

    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
                      Settings().get('google_docs_api_credentials_filepath'), self.scope)

        self.gc = gspread.authorize(credentials)

    def get_df(self, sheet_name):
        wks = self.gc.open(sheet_name).sheet1
        return pd.DataFrame(wks.get_all_records())
