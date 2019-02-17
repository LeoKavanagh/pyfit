import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import os
import requests
from flask import request
import json
import datetime as dt
import pandas as pd


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


def get_dataset(credentials, start_date, end_date, data_source):

    start_time_nanos = get_epoch(start_date, scale='nanos')
    end_time_nanos = get_epoch(end_date, scale='nanos')
    data_set = "{0}-{1}".format(end_time_nanos, start_time_nanos)

    fitness = build('fitness', 'v1', credentials=credentials)

    dat = fitness \
        .users() \
        .dataSources() \
        .datasets() \
        .get(userId='me', dataSourceId=data_source, datasetId=data_set) \
        .execute()

    return dat
