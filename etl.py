import pandas as pd
import datetime as dt

from authorise import authorize
from tmp import (get_data_sources, get_steps_request, process_steps,
				 get_agg, get_dataset, process_heart, process_sleep)

# connect
access_token = authorize()

# set up
start_date = dt.date(2018, 8, 1)
end_date =  dt.date.today() - dt.timedelta(days=1)

# download
step_request_body = get_steps_request(start_date, end_date)
raw_steps = get_agg(step_request_body, access_token)

# heart_data_source = 'raw:com.google.heart_rate.bpm:Mobvoi:TicWatch Pro:4841d82c20298413:PAH8011 heart rate PPG'
# heart_data_source = 'raw:com.google.heart_rate.bpm:Mobvoi:TicWatch Pro:4841d82c20298413:Heart Rate PPG'
# heart_data_source = 'derived:com.google.heart_minutes:com.google.android.gms:bout_filtered_5min<-merge_heart_minutes'
# heart_data_source = 'derived:com.google.heart_rate.bpm:com.google.android.gms:interpolated_heart_rate<-merge_heart_rate_bpm 27160'
heart_data_source = 'derived:com.google.heart_rate.bpm:com.mobvoi.companion.aw:com.mobvoi.companion.awcom.google.heart_rate.bpm'
heart = get_dataset(access_token, start_date, end_date, heart_data_source)   

# sleep_data_source = 'derived:com.google.activity.segment:com.urbandroid.sleep:session_activity_segment'
sleep_data_source = 'raw:com.google.activity.segment:com.urbandroid.sleep:'
sleep = get_dataset(access_token, start_date, end_date, sleep_data_source)


# process
steps_df = process_steps(raw_steps)
print(steps_df.head())

heart_df = process_heart(heart)
print(heart_df.head())

sleep_df = process_sleep(sleep)
print(sleep_df.head())

df = steps_df \
    .join(heart_df, how='inner') \
    .join(sleep_df, how='inner') \
    [['steps', 'mean_heart_rate', 'heart_rate_sdev', 'awake', 'deep_sleep', 'light_sleep', 'rem_sleep', 'unknown']]

print(df.head())
