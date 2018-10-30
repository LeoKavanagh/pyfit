import os
import glob
import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime as dt

"""
Fitbit API limits to 150 calls per hour
https://towardsdatascience.com/
collect-your-own-fitbit-data-with-python-ff145fa10873
"""

FITBIT_CLIENT_ID = os.environ['FITBIT_CLIENT_ID']
FITBIT_CLIENT_SECRET = os.environ['FITBIT_CLIENT_SECRET']

server = Oauth2.OAuth2Server(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET)
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

auth2_client = fitbit.Fitbit(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET,
                             oauth2=True, access_token=ACCESS_TOKEN,
                             refresh_token=REFRESH_TOKEN)

# Want to use the latest version of the Fitbit API 
# so do a kind of hotfix on the fitbit library
def _get_common_args():
    return ('https://api.fitbit.com', 1.2, '-')

auth2_client._get_common_args = _get_common_args

def get_sleep_range(start_date, end_date):
    """
    https://dev.fitbit.com/docs/sleep/#get-sleep-logs
    date should be a datetime.date object.
    """

    url = "{0}/{1}/user/-/sleep/date/{start_date}/{end_date}.json".format(
        *auth2_client._get_common_args(),
        start_date=start_date,
        end_date=end_date
    )
    return auth2_client.make_request(url)

auth2_client.get_sleep_range = get_sleep_range

start_date = dt.date(2018, 1, 1)
day_date = start_date + dt.timedelta(99)
end_date = dt.date(2018, 8, 1)

sleep_range = auth2_client \
    .get_sleep_range(start_date.strftime('%Y-%m-%d'),
                     day_date.strftime('%Y-%m-%d'))

sleep_df = pd.DataFrame((x['dateOfSleep'], x['duration'], x['efficiency'], 
    x['minutesAwake'], x['minutesAsleep'],
    x['levels']['summary'].get('deep', {'minutes': 0})['minutes'],
    x['levels']['summary'].get('light', {'minutes': 0})['minutes'],
    x['levels']['summary'].get('rem', {'minutes': 0})['minutes'],
    x['levels']['summary'].get('wake', {'minutes': 0})['minutes'])
    for x in sleep_range['sleep'])

sleep_df.columns = ['date', 'duration', 'efficiency', 'minutesAwake',
'minutesAsleep', 'minutesDeepSleep', 'minutesLightSleep', 'minutesREMSleep',
'minutesWake']

final_sleep_df = sleep_df.copy()


while day_date <= end_date:

    days_to_end_date = (end_date - day_date).days
    increment = min(days_to_end_date, 99)

    new_start_date = day_date
    day_date += dt.timedelta(days=increment)


    sleep_range = auth2_client \
        .get_sleep_range(new_start_date.strftime('%Y-%m-%d'),
                         day_date.strftime('%Y-%m-%d'))

    sleep_df = pd.DataFrame((x['dateOfSleep'], x['duration'], x['efficiency'],
        x['minutesAwake'], x['minutesAsleep'],
        x['levels']['summary'].get('deep', {'minutes': 0})['minutes'],
        x['levels']['summary'].get('light', {'minutes': 0})['minutes'],
        x['levels']['summary'].get('rem', {'minutes': 0})['minutes'],
        x['levels']['summary'].get('wake', {'minutes': 0})['minutes'])
        for x in sleep_range['sleep'])

    sleep_df.columns = ['date', 'duration', 'efficiency', 'minutesAwake',
    'minutesAsleep', 'minutesDeepSleep', 'minutesLightSleep',
    'minutesREMSleep', 'minutesWake']

    final_sleep_df = final_sleep_df.append(sleep_df)

final_sleep_df.to_csv('data/fitbit/sleep/all_sleep.csv')

