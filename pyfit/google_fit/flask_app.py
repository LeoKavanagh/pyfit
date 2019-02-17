# -*- coding: utf-8 -*-

import os
import json
import pickle
import flask
import datetime as dt

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

app = flask.Flask(__name__)
app.secret_key = os.environ['PYFIT_FLASK_SECRET_KEY']

CLIENT_SECRETS_FILE = os.environ['GOOGLE_WEB_APPLICATION_CREDENTIALS']

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/fitness.body.read',
          'https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/fitness.blood_pressure.read',
          'https://www.googleapis.com/auth/fitness.nutrition.write',
          'https://www.googleapis.com/auth/fitness.body.write',
          'https://www.googleapis.com/auth/fitness.blood_pressure.write',
          'https://www.googleapis.com/auth/fitness.reproductive_health.read',
          'https://www.googleapis.com/auth/fitness.activity.read',
          'https://www.googleapis.com/auth/fitness.body_temperature.write',
          'https://www.googleapis.com/auth/fitness.reproductive_health.write',
          'https://www.googleapis.com/auth/fitness.blood_glucose.read',
          'https://www.googleapis.com/auth/fitness.location.read',
          'https://www.googleapis.com/auth/fitness.blood_glucose.write',
          'https://www.googleapis.com/auth/fitness.body_temperature.read',
          'https://www.googleapis.com/auth/fitness.oxygen_saturation.write',
          'https://www.googleapis.com/auth/fitness.activity.write',
          'https://www.googleapis.com/auth/fitness.nutrition.read',
          'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
          'https://www.googleapis.com/auth/fitness.location.write']

API_SERVICE_NAME = 'fitness'
API_VERSION = 'v1'

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/authorize">Authorise</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/test">Test heart data API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '</td></tr></table>')


@app.route('/')
def index():
    """
    Life is too short to do this properly
    """
    return print_index_table()

@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    print(credentials_to_dict(credentials))

    fitness = googleapiclient \
        .discovery \
        .build('fitness', 'v1', credentials=credentials)

    heart_data_source = ('derived:com.google.heart_rate.bpm:'
                        'com.google.android.gms:merge_heart_rate_bpm')

    today = dt.date.today()       
    yesterday = today - dt.timedelta(days=1)

    start = int(yesterday.strftime("%s")) * 1000000000
    end = int(today.strftime("%s")) * 1000000000

    assert end > start

    data_set = "{0}-{1}".format(end, start)

    heart_data = fitness \
        .users() \
        .dataSources() \
        .datasets() \
        .get(userId='me', dataSourceId=heart_data_source, datasetId=data_set) \
        .execute()

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(**heart_data)


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        # apparently we also need this to get a refresh token
        # see https://github.com/googleapis/google-api-python-client/issues/213
        prompt='consent')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials

    credentials_dict = credentials_to_dict(credentials)

    with open('credentials.pickle', 'wb') as f:
        pickle.dump(credentials, f)

    with open('credentials_dict.json', 'w') as f:
        json.dump(credentials_dict, f)

    flask.session['credentials'] = credentials_dict

    return flask.redirect(flask.url_for('test_api_request'))


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    # When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('0.0.0.0', 8080, debug=True)
