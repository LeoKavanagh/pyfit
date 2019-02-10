import pandas as pd
import datetime as dt
import json


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

    # Fitbit deep_sleep_prop seems to be 33% of the size
    # of the Sleep As Android one. Adjust accordingly
    deep_sleep_adj = 0.333

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

    sleep_df.deep_sleep_prop = sleep_df.deep_sleep_prop * deep_sleep_adj
    sleep_df['dsp_lag'] = sleep_df.deep_sleep_prop.shift(1)

    return sleep_df


def clean_google_data(raw_heart_data, raw_sleep_data):
    """
    JSON from Google Fitness API loaded as Python dict

    :param raw_heart_data: python dict
    :param raw_sleep_data: python dict
    """

    heart_df = process_heart(raw_heart_data)
    sleep_df = process_sleep(raw_sleep_data)

    df = heart_df.join(sleep_df, how='inner')

    df.columns = ['mean_rate', 'sd_rate', 'rate_range',
                  'minutesAwake', 'minutesDeepSleep', 'minutesLightSleep',
                  'minutesREMSleep', 'deep_sleep_prop', 'dsp_lag']

    return df

def save_data(df, path):
    """
    Side effect function to be expanded later to handle S3, GCP etc
    :param df: pandas dataframe
    """

    df.to_csv(path)


def main():

    with open('data/google/google_heart.json', 'r') as f:
        raw_heart_data = json.load(f)

    with open('data/google/google_sleep.json', 'r') as f:
        raw_sleep_data = json.load(f)

    processed_data = clean_google_data(raw_heart_data, raw_sleep_data)
    save_data(processed_data, 'datasets/google_training_data.csv')

if __name__=='main':
    main()