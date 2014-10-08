#!/usr/bin/env python3

import json
import os
import pyperclip

from requests_oauthlib import OAuth2Session

#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
class gt:
    def __init__(self):
        json_location = os.path.join(os.path.dirname(__file__), 'credentials.json')
        with open(json_location) as jFile:
            credentials = json.load(jFile).get('installed', None)

        if not credentials:
            raise Exception('No valid Credentials file found.')

        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        redirect_uri = credentials['redirect_uris'][0]
        auth_url = credentials['auth_uri']

        scope = ['https://www.googleapis.com/auth/tasks',
                'https://www.googleapis.com/auth/tasks.readonly']
        token_url = 'https://accounts.google.com/o/oauth2/token'

        self.google = OAuth2Session(client_id, redirect_uri=redirect_uri,
                scope=scope)

        authorization_url, __ = self.google.authorization_url( auth_url,
                access_type="offline", approval_prompt="force")

        pyperclip.copy(authorization_url)

        redirect_response = input(
                'The following URL has been copied into your clipboard:'
                '\n\n{}\n\nPlease visit the url and paste the response code '
                'below:\n'.format(authorization_url))

        self.google.fetch_token(token_url, client_secret=client_secret,
                code=redirect_response)

        tasks = self.google.get('https://www.googleapis.com/tasks/v1/lists/@default/tasks').json()
        print(tasks)

if __name__ == '__main__':
    gt()
