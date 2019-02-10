import google.oauth2.credentials
import google_auth_oauthlib.flow
import os
import requests
from flask import request
import json
import datetime as dt
import pandas as pd
from authorise import authorize
from google_fit_utils import (get_steps_request,
                              get_agg,
                              get_dataset)

def download_google_data_batch(access_token):
    """
    :param access_token: string. from oath2
    :return: None
    """

    # Date the google data starts
    start_date = dt.date(2018, 8, 1)

    end_date =  dt.date.today() - dt.timedelta(days=1)

    heart_data_source = ('derived:com.google.heart_rate.bpm:'
                         'com.google.android.gms:merge_heart_rate_bpm')
    heart = get_dataset(access_token, start_date,
                        end_date, heart_data_source)

    with open('data/google/google_heart.json', 'w') as f:
        json.dump(heart, f)

    sleep_data_source = ('raw:com.google.activity.'
                         'segment:com.urbandroid.sleep:')
    sleep = get_dataset(access_token, start_date,
                        end_date, sleep_data_source)

    with open('data/google/google_sleep.json', 'w') as f:
        json.dump(sleep, f)


def main():

    access_token = authorize()
    download_google_data_batch(access_token)


if __name__ == "__main__":
    main()
