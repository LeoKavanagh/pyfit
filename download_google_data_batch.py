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

def main():
    
    secrets_file = os.environ['GOOGLE_WEB_APPLICATION_CREDENTIALS']
    access_token = authorize()

    start_date = dt.date(2018, 8, 1)
    end_date =  dt.date.today() - dt.timedelta(days=1)

    # There's seemingly a limit to the range allowed in an aggregate dataset
    # but it's not at all clear from the documentation what this limit is.
    
    # step_request_body = get_steps_request(start_date, end_date)
    # steps = get_agg(step_request_body, access_token)

    # with open('data/google/google_steps.json', 'w') as f:
    #     json.dump(steps, f)

    heart_data_source = 'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm'
    heart = get_dataset(access_token, start_date, 
                        end_date, heart_data_source)   

    with open('data/google/google_heart.json', 'w') as f:
        json.dump(heart, f)
    
    sleep_data_source = 'raw:com.google.activity.segment:com.urbandroid.sleep:'
    sleep = get_dataset(access_token, start_date, 
                        end_date, sleep_data_source)

    with open('data/google/google_sleep.json', 'w') as f:
        json.dump(sleep, f)

if __name__ == "__main__":
    main()
