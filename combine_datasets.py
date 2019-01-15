import pandas as pd
import datetime as dt

fitbit_df = pd.read_csv('datasets/processed_fitbit_df.csv') \
    [["date","mean_rate","sd_rate","rate_range",
      "deep_sleep_prop","dsp_lag"]]

google_df = pd.read_csv('datasets/google_training_data.csv') \
    [["date","mean_rate","sd_rate","rate_range",
      "deep_sleep_prop","dsp_lag"]]

df = pd.concat([fitbit_df, google_df])

df.to_csv('datasets/combined_data.csv')
