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


def process_steps(steps_dict):
    """
    """

    steps = steps_dict['bucket']

    steps_data = [(x['dataset'][0]['point'][0]['startTimeNanos'],
                   x['dataset'][0]['point'][0]['value'][0]['intVal'])
                  for x in steps] 

    steps_df = pd.DataFrame(steps_data)
    steps_df.columns = ['timestamp', 'steps']
    steps_df['datetime'] = steps_df['timestamp'] \
        .apply(lambda x: pd.to_datetime(int(x), unit='ns'))
    steps_df['date'] = steps_df['datetime'] \
        .apply(lambda x: pd.datetime.date(x))

    steps_df = steps_df.set_index('date')

    return steps_df

def process_heart(heart_dict):
    """
    """

    heart = heart_dict['point']

    heart_data = [(x['startTimeNanos'], x['value'][0]['fpVal']) for x in heart]
    heart_df = pd.DataFrame(heart_data)

    heart_df.columns = ['timestamp', 'heart_rate']
    heart_df['datetime'] = heart_df['timestamp'] \
        .apply(lambda x: pd.to_datetime(int(x), unit='ns'))

    heart_df['date'] = heart_df['datetime'] \
        .apply(lambda x: pd.datetime.date(x))
    
    heart_df = heart_df.set_index('date')

    # day of week
    heart_df['dow'] = heart_df['datetime'].dt.day_name()


    hr_by_day = heart_df.groupby('date')
    heart_df['mean_heart_rate'] = hr_by_day.heart_rate.mean()
    heart_df['heart_rate_sdev'] = hr_by_day.heart_rate.std()
    heart_df['heart_rate_range'] = (hr_by_day.heart_rate.max() -
                                    hr_by_day.heart_rate.min())

    heart_df= heart_df[['mean_heart_rate', 'heart_rate_sdev',
                        'heart_rate_range']] \
        .drop_duplicates()

    return heart_df

def process_sleep(sleep_dict):

    # google gives us these stages in nanoseconds
    sleep_types = {
        '4': 'unknown',
        '109': 'minutesLightSleep',
        '110': 'minutesDeepSleep',
        '111': 'minutesREMSleep',
        '112': 'minutesAwake'
    }

    sleep = sleep_dict['point']

    sleep_data = [(x['startTimeNanos'], x['endTimeNanos'],
                   str(x['value'][0]['intVal'])) for x in sleep]
    sleep_df = pd.DataFrame(sleep_data)

    sleep_df.columns = ['start_timestamp', 'end_timestamp', 'sleep_type']
    
    sleep_df['sleep_type_name'] = sleep_df['sleep_type'].map(sleep_types)

    sleep_df['start_datetime'] = sleep_df['start_timestamp'] \
        .apply(lambda x: pd.to_datetime(int(x), unit='ns'))
    sleep_df['end_datetime'] = sleep_df['end_timestamp'] \
        .apply(lambda x: pd.to_datetime(int(x), unit='ns'))

    # from nanoseconds to minutes
    sleep_df['duration'] = sleep_df \
        .apply(lambda x: (int(x['end_timestamp']) - 
                          int(x['start_timestamp']))/(60 * 1000000000), axis=1)

    # not sure if groupby by date is the right thing to do.
    # Maybe group midday to midday
    sleep_df['date'] = sleep_df['start_datetime'] \
        .apply(lambda x: pd.datetime.date(x) - dt.timedelta(hours=12))
    
    gb_sleep = sleep_df.groupby(['date', 'sleep_type_name'])
    sleep_by_type = gb_sleep.duration.sum().reset_index('sleep_type_name')

    sleep_df = sleep_by_type.reset_index() \
        .pivot(index='date', columns='sleep_type_name', values='duration') \
        .reset_index() \
        .set_index('date') \
        .drop('unknown', axis=1)

    # proportion of time spend in deep sleep
    # sleep_df['deep_sleep_prop'] = sleep_df \
    #     .minutesDeepSleep/(sleep_df.minutesDeepSleep + 
    #                        sleep_df.minutesLightSleep +
    #                        sleep_df.minutesREMSleep + 
    #                        sleep_df.minutesAwake)

    sleep_df['deep_sleep_prop'] = sleep_df \
        .minutesDeepSleep/(sleep_df.minutesDeepSleep + 
                           sleep_df.minutesLightSleep)

    return sleep_df


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

#def main():
#
#    secrets_file = os.environ['GOOGLE_WEB_APPLICATION_CREDENTIALS']
#    access_token = authorize()
#
#    data_sources = get_data_sources(access_token)
#
#    sleep_sources = [a['dataStreamId'] for a in data_sources['dataSource'] 
#                     if 'sleep' in a['dataStreamId']]
#    heart_sources = [a['dataStreamId'] for a in data_sources['dataSource'] 
#                     if 'heart' in a['dataStreamId']]
#
#    # Roughly when I started wearing the WearOS watch
#    start_date = dt.date(2018, 8, 1)
#    end_date =  dt.date.today() - dt.timedelta(days=1)
#
#    # step_request_body = get_steps_request(start_date, end_date)
#    # steps = get_agg(step_request_body, access_token)
#    # print(steps)
#
#    heart_data_source = ('raw:com.google.heart_rate.bpm:Mobvoi:TicWatch Pro:'
#                        '4841d82c20298413:PAH8011 heart rate PPG')
#    heart = get_dataset(access_token, start_date, end_date, heart_data_source)
#    heart_df = process_heart(heart)
#
#    sleep_request_body = get_sleep_request(start_date, end_date)
#    sleep = get_agg(sleep_request_body, access_token)
#    print(sleep)
#
#
#
#if __name__ == "__main__":
#    main()
