#!/usr/bin/env python3

import json
import os
import sys
import webbrowser
from pprint import pprint
from time import time

import keyring
from requests_oauthlib import OAuth2Session
from strict_rfc3339 import timestamp_to_rfc3339_utcoffset, validate_rfc3339

#import timeconversion as tc
from task import Task
from tasklist import TaskList

class Gtasks:
    SCOPE = ['https://www.googleapis.com/auth/tasks',
            'https://www.googleapis.com/auth/tasks.readonly']
    AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    TASKS_URL = 'https://www.googleapis.com/tasks/v1/lists/{}/tasks'
    LISTS_URL = 'https://www.googleapis.com/tasks/v1/users/@me/lists'

    def __init__(self, identifier='default', auto_push=True, auto_pull=False,
            open_browser=True, credentials_location=None):
        self.identifier = identifier
        self.auto_push = auto_push
        self.auto_pull = auto_pull
        self.open_browser = open_browser
        self._task_index = {}
        self._list_index = {}

        self.credentials_location = (credentials_location or
                os.path.join(os.path.dirname(__file__), 'credentials.json'))
        self.load_credentials()

        refresh_token = keyring.get_password('gtasks.py', self.identifier)
        if refresh_token:
            self.refresh_authentication(refresh_token)
        else:
            self.authenticate()

    def load_credentials(self):
        with open(self.credentials_location) as json_creds:
            credentials = json.load(json_creds).get('installed', None)

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
            webbrowser.open_new_tab(authorization_url)
            prompt = ('The following URL has been opened in your web browser:'
                    '\n\n{}\n\nPlease paste the response code below:\n')
        else:
            prompt = ('Please copy the following URL into your web browser:'
                    '\n\n{}\n\nPlease paste the response code below:\n')

        redirect_response = safe_input(prompt.format(authorization_url))
        print('Thank you!')

        tokens = self.google.fetch_token(Gtasks.TOKEN_URL,
                client_secret=self.client_secret, code=redirect_response)
        keyring.set_password('gtasks.py', self.identifier, tokens['refresh_token'])

    def _download_items(self, url, parameters, item_type, item_index, max_results):
        results = []
        while True:
            whats_left = max_results - len(results)
            parameters['maxResults'] = min(whats_left, 100)

            response = self.google.get(url, params=parameters).json()
            for item_dict in response['items']:
                item_id = item_dict['id'] 
                if item_id in item_index:
                    item = item_index[item_id]
                    item._dict = item_dict
                else:
                    item = item_type(item_dict, self)
                results.append(task)

            if 'nextPageToken' in response and len(results) < max_results:
                parameters['pageToken'] = response['nextPageToken']
            else:
                break
        return results

    def tasks(self, task_list='@default', max_results=float('inf'),
            due_min=None, due_max=None, completed_min=None, completed_max=None,
            include_completed=True, include_deleted=False, include_hidden=False):
        url = Gtasks.TASKS_URL.format(task_list)
        parameters = {
                'showCompleted': include_completed,
                'showDeleted': include_deleted,
                'showHidden': include_hidden,
                }
        return self._download_items(url, parameters, Task, self._task_index,
                max_results)

    def lists(self):
        parameters = {}
        return self._download_items(Gtasks.LISTS_URL, parameters, TaskList,
                self._list_index, max_results)

def safe_input(prompt):
    if sys.version_info[0] == 2:
        return raw_input(prompt)
    else:
        return input(prompt)

if __name__ == '__main__':
    gt = Gtasks()
    tasks = gt.tasks(include_completed=False)
    #tasks = gt.tasks(max_results=10)
    #pprint(tasks)
    for t in tasks:
        print(t)
        t.title = t.title + ' banana'
        print(t)
