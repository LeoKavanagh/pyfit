import pandas as pd
import datetime as dt
import json
from google_fit_utils import (process_heart, process_sleep,
                              process_steps, get_epoch)

# Fitbit deep_sleep_prop seems to be 33% of the size
# of the Sleep As Android one. Adjust accordingly
deep_sleep_adj = 0.333

# process
with open('data/google/google_steps.json', 'r') as f:
    steps_dict = json.load(f)

steps_df = process_steps(steps_dict)

with open('data/google/google_heart.json', 'r') as f:
    heart_dict = json.load(f)

heart_df = process_heart(heart_dict)

with open('data/google/google_sleep.json', 'r') as f:
    sleep_dict = json.load(f)

sleep_df = process_sleep(sleep_dict)

df = steps_df \
    .join(heart_df, how='inner') \
    .join(sleep_df, how='inner') \
    .drop('timestamp', axis=1) \
    .drop('datetime', axis=1)

df.columns = ['steps', 'mean_rate', 'sd_rate', 'minutesAwake', 
              'minutesDeepSleep', 'minutesLightSleep', 'minutesREMSleep',
              'deep_sleep_prop']

df.deep_sleep_prop = df.deep_sleep_prop * deep_sleep_adj

print(df.head())
df.to_csv('datasets/google_training_data.csv')
