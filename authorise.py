import google.oauth2.credentials
import google_auth_oauthlib.flow
import os
import requests
from flask import request
import json
import datetime as dt
import subprocess
from requests.exceptions import ConnectionError


def get_authorization_url(secrets_file):

    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        secrets_file,
        scopes=['https://www.googleapis.com/auth/fitness.activity.read',
                'https://www.googleapis.com/auth/fitness.activity.write',
                'https://www.googleapis.com/auth/fitness.blood_glucose.read',
                'https://www.googleapis.com/auth/fitness.blood_glucose.write',
                'https://www.googleapis.com/auth/fitness.blood_pressure.read',
                'https://www.googleapis.com/auth/fitness.blood_pressure.write',
                'https://www.googleapis.com/auth/fitness.body.read',
                'https://www.googleapis.com/auth/fitness.body.write',
                'https://www.googleapis.com/auth/fitness.body_temperature.read',
                'https://www.googleapis.com/auth/fitness.body_temperature.write',
                'https://www.googleapis.com/auth/fitness.location.read',
                'https://www.googleapis.com/auth/fitness.location.write',
                'https://www.googleapis.com/auth/fitness.nutrition.read',
                'https://www.googleapis.com/auth/fitness.nutrition.write',
                'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
                'https://www.googleapis.com/auth/fitness.oxygen_saturation.write',
                'https://www.googleapis.com/auth/fitness.reproductive_health.read',
                'https://www.googleapis.com/auth/fitness.reproductive_health.write'])


    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required.
    flow.redirect_uri = 'http://localhost:8080'

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # next_step = "Go here next: {}".format(authorization_url)
    # return next_step
    return authorization_url


def get_access_token(secrets_file, code):

    with open(secrets_file, 'r') as f:
              things = json.load(f)

    url = 'https://www.googleapis.com/oauth2/v4/token'

    data = {'code': code,
            'client_id': things['web']['client_id'],
            'client_secret': things['web']['client_secret'],
            'redirect_uri': things['web']['redirect_uris'][0],
            'grant_type': 'authorization_code'}

    r = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)

    access_token = json.loads(r.content.decode('utf-8')).get('access_token')

    return access_token


def authorize():

    try:    
        r = requests.get('http://0.0.0.0:8080')
        print('done')
    except ConnectionError:
        raise ConnectionError('Turn on the flask server')


    secrets_file = os.environ['GOOGLE_WEB_APPLICATION_CREDENTIALS']
    auth_url = get_authorization_url(secrets_file)
    print('Go to {}'.format(auth_url))

    code = input('\n\nEnter the code: ')
    access_token = get_access_token(secrets_file, code)

    print(access_token)
    return access_token


if __name__ == "__main__":
    authorize()
