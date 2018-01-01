import pandas as pd

from risk_salon_tools.services.google_docs import SheetsClient


def _get_all_responses():
    sheets_client = SheetsClient()
    responses = sheets_client.get_df('[Risk Salon] Topics of Interest Survey (Responses)')
    responses_df = pd.concat([responses,
                              responses['What topics do you find interesting?'] \
                             .str.get_dummies(sep=', ')], axis='columns')
    responses_df['Email Address'] = responses_df['Email Address'].str.lower()
    return responses_df


def get_latest_responses():
    responses = _get_all_responses().sort_values('Timestamp', ascending=False). \
        groupby('Email Address').nth(0).reset_index(). \
        set_index(['Email Address', 'First Name', 'Last Name', 'Timestamp']).reset_index()
    return responses.drop(['Imported from Doodle?', 'What topics do you find interesting?'],
                          axis='columns').\
                          rename(columns={'Timestamp':'Survey Timestamp'})
