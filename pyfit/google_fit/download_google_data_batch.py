import google.oauth2.credentials
import google_auth_oauthlib.flow

import datetime as dt
import pickle
from googleapiclient.discovery import build

import os
import json
from google_fit_utils import get_epoch, get_dataset

def download_google_data_batch(credentials):
    """
    :param credentials: from oath2. must have refresh token
    :return: None
    """

    # Roughly the date the google data starts - 
    # when I bought the smartwatch
    start_date = dt.date(2018, 8, 1)

    end_date =  dt.date.today() - dt.timedelta(days=1)

    heart_data_source = ('derived:com.google.heart_rate.bpm:'
                         'com.google.android.gms:merge_heart_rate_bpm')
    heart = get_dataset(credentials, start_date,
                        end_date, heart_data_source)

    with open('data/google/google_heart.json', 'w') as f:
        json.dump(heart, f)

    sleep_data_source = ('raw:com.google.activity.'
                         'segment:com.urbandroid.sleep:')
    sleep = get_dataset(credentials, start_date,
                        end_date, sleep_data_source)

    with open('data/google/google_sleep.json', 'w') as f:
        json.dump(sleep, f)


def main():

    with open('/home/leo/repos/pyfit/credentials.pickle', 'rb') as f:
        credentials = pickle.load(f)

    download_google_data_batch(credentials)


if __name__ == "__main__":
    main()
