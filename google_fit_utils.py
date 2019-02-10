import google.oauth2.credentials
import google_auth_oauthlib.flow
import os
import requests
from flask import request
import json
import datetime as dt
import pandas as pd
from authorise import authorize


def get_data_sources(access_token):
    headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {}'.format(access_token)}

    url = 'https://www.googleapis.com/fitness/v1/users/me/dataSources'

    resp = requests.get(url, headers=headers)

    dat = json.loads(resp.content.decode('utf-8'))

    return dat

def get_epoch(date_object, scale='millis'):

    factors = {'seconds': 1,
               'millis': 1000,
               'nanos': 1000000000}
    
    mult = factors[scale]

    return int(date_object.strftime("%s")) * mult


def get_steps_request(start_date, end_date):

    start_time = get_epoch(start_date)
    end_time = get_epoch(end_date)

    data = {"aggregateBy": [{
                    "dataTypeName": "com.google.step_count.delta",
                    "dataSourceId": "derived:com.google.step_count.delta"
                                    ":com.google.android.gms:"
                                    "estimated_steps"}],
               "bucketByTime": { "durationMillis": 86400000 },
               "startTimeMillis": start_time,
               "endTimeMillis": end_time}
    
    return data


def get_agg(request_body, access_token):

    url = 'https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate'

    headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {}'.format(access_token)}


    resp = requests.post(url, headers=headers, json=request_body)
    dat = json.loads(resp.content.decode('utf-8'))

    return dat


def get_dataset(access_token, start_date, end_date, data_source):

    headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {}'.format(access_token)}

    start_time_nanos = get_epoch(start_date, scale='nanos')
    end_time_nanos = get_epoch(end_date, scale='nanos')

    base = 'https://www.googleapis.com/fitness/v1/users/me/dataSources/'

    url = base + data_source + '/datasets/' \
        + str(end_time_nanos) \
        + '-' + str(start_time_nanos)        

    resp = requests.get(url, headers=headers)
    dat = json.loads(resp.content.decode('utf-8'))

    return dat
