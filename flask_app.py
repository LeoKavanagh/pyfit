# -*- coding: utf-8 -*-

import os
import flask
import requests
from flask import request

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.


@app.route('/')
def index():
  """
  Life is too short to do this properly
  """
  # state = request.args.get('state', None)
  code = request.args.get('code', None)

  return ('{}'.format(code))


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  # When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('0.0.0.0', 8080, debug=True)

