import pandas as pd

from risk_salon_tools.services.google_docs import SheetsClient


def get_responses():
    sheets_client = SheetsClient()
    responses = sheets_client.get_df('[Risk Salon] Topics of Interest Survey (Responses)')
    return pd.concat([responses,
                      responses['What topics do you find interesting?']\
                      .str.get_dummies(sep=', ')], axis='columns')
