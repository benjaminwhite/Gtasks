#!/usr/bin/env python3

import json
import keyring
import os
import webbrowser

from pprint import pprint
from time import time

from requests_oauthlib import OAuth2Session

class Gtasks:
    SCOPE = ['https://www.googleapis.com/auth/tasks',
            'https://www.googleapis.com/auth/tasks.readonly']
    AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

    def __init__(self, account='default', open_browser=True):
        self.account = account
        self.load_credentials()

        self.open_browser = open_browser

        refresh_token = keyring.get_password('gtasks.py', self.account)

        if refresh_token:
            self.refresh_authentication(refresh_token)
        else:
            self.authenticate()

    def load_credentials(self):
        json_location = os.path.join(os.path.dirname(__file__),
                'credentials.json')

        with open(json_location) as jFile:
            credentials = json.load(jFile).get('installed', None)

        if credentials:
            self.client_id = credentials['client_id']
            self.client_secret = credentials['client_secret']
            self.redirect_uri = credentials['redirect_uris'][0]
        else:
            raise Exception('No valid Credentials file found.')

    def refresh_authentication(self, refresh_token):
        extra = {'client_id': self.client_id, 'client_secret': self.client_secret}

        self.google = OAuth2Session(self.client_id, scope=Gtasks.SCOPE,
                redirect_uri=self.redirect_uri, auto_refresh_kwargs=extra)

        self.google.refresh_token(Gtasks.TOKEN_URL, refresh_token)

    def authenticate(self):
        self.google = OAuth2Session(self.client_id, scope=Gtasks.SCOPE,
                redirect_uri=self.redirect_uri)

        authorization_url, __ = self.google.authorization_url(Gtasks.AUTH_URL,
                access_type='offline', approval_prompt='force')

        if self.open_browser:
            print('The following URL has been opened in your web browser:\n')
            webbrowser.open_new_tab(authorization_url)
        else:
            print('Please copy the following URL into your web browser:\n')

        print(authorization_url)

        redirect_response = input('\nPlease paste the response code below:\n')

        tokens = self.google.fetch_token(Gtasks.TOKEN_URL,
                client_secret=self.client_secret, code=redirect_response)

        keyring.set_password('gtasks.py', self.account, tokens['refresh_token'])

        print('Thank you!')

    def tasks(self, task_list='@default'):
        tasks = self.google.get('https://www.googleapis.com/tasks/v1/lists/{}'
                '/tasks'.format(task_list)).json()
        return tasks

#class Task:
    #def from_dict(json_dict):
        #pass

if __name__ == '__main__':
    gt = Gtasks()
    pprint(gt.tasks())
