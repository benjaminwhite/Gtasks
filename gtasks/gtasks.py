from __future__ import absolute_import

import json
import os
import webbrowser
from contextlib import contextmanager

import keyring
from requests_oauthlib import OAuth2Session

import gtasks.timeconversion as tc
from gtasks.misc import compatible_input
from gtasks.task import Task
from gtasks.tasklist import TaskList

class Gtasks(object):
    SCOPE = ['https://www.googleapis.com/auth/tasks',
            'https://www.googleapis.com/auth/tasks.readonly']
    AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    LISTS_URL = 'https://www.googleapis.com/tasks/v1/users/@me/lists'
    TASKS_URL = 'https://www.googleapis.com/tasks/v1/lists/{}/tasks/'

    def __init__(self, identifier='default', auto_push=True, auto_pull=False,
            open_browser=True, force_login=False, credentials_location=None):
        self.identifier = identifier
        self.auto_push = auto_push
        self.auto_pull = auto_pull
        self.open_browser = open_browser
        self.force_login = force_login
        self.credentials_location = (credentials_location or
                os.path.join(os.path.dirname(__file__), 'credentials.json'))
        self._list_index = {}
        self._task_index = {}
        self._updates = set()

        self.load_credentials()
        self.authenticate()

    def load_credentials(self):
        with open(self.credentials_location) as json_creds:
            credentials = json.load(json_creds).get('installed', None)
        if credentials:
            self.client_id = credentials['client_id']
            self.client_secret = credentials['client_secret']
            self.redirect_uri = credentials['redirect_uris'][0]
        else:
            raise IOError('No valid Credentials file found.')

    def authenticate(self):
        extra = {'client_id': self.client_id, 'client_secret': self.client_secret}
        self.google = OAuth2Session(self.client_id, scope=Gtasks.SCOPE,
                redirect_uri=self.redirect_uri, auto_refresh_kwargs=extra,
                auto_refresh_url=Gtasks.TOKEN_URL, token_updater=lambda t: None)

        refresh_token = keyring.get_password('gtasks.py', self.identifier)
        if refresh_token and not self.force_login:
            self.google.refresh_token(Gtasks.TOKEN_URL, refresh_token)
        else:
            authorization_url, __ = self.google.authorization_url(Gtasks.AUTH_URL,
                    access_type='offline', approval_prompt='force')

            if self.open_browser:
                webbrowser.open_new_tab(authorization_url)
                prompt = ('The following URL has been opened in your web browser:'
                        '\n\n{}\n\nPlease paste the response code below:\n')
            else:
                prompt = ('Please copy the following URL into your web browser:'
                        '\n\n{}\n\nPlease paste the response code below:\n')
            redirect_response = compatible_input(prompt.format(authorization_url))
            print('Thank you!')

            tokens = self.google.fetch_token(Gtasks.TOKEN_URL,
                    client_secret=self.client_secret, code=redirect_response)
            keyring.set_password('gtasks.py', self.identifier,
                    tokens['refresh_token'])

    def _download_items(self, url, params, item_type, item_index, max_results):
        results = []
        while True:
            whats_left = max_results - len(results)
            params['maxResults'] = min(whats_left, 100)

            response = self.google.get(url, params=params)
            response.raise_for_status()
            response_dict = response.json()
            for item_dict in response_dict.get('items', ()):
                item_id = item_dict['id']
                if item_id in item_index:
                    item = item_index[item_id]
                    item._dict = item_dict
                else:
                    item = item_type(item_dict, self)
                results.append(item)
            if 'nextPageToken' in response_dict and len(results) < max_results:
                params['pageToken'] = response_dict['nextPageToken']
            else:
                break
        return results

    def get_tasks(self, include_completed=True, due_min=None, due_max=None,
            task_list='@default', max_results=float('inf'), updated_min=None,
            completed_min=None, completed_max=None, include_deleted=False,
            include_hidden=False):
        params = {}
        if not include_completed:
            params['showCompleted'] = include_completed
        if due_min:
            params['dueMin'] = tc.to_date_rfc3339(due_min)
        if due_max:
            params['dueMax'] = tc.to_date_rfc3339(due_max, plus_a_min=True)
        if updated_min:
            params['updatedMin'] = tc.to_rfc3339(updated_min)
        if completed_min:
            params['completedMin'] = tc.to_rfc3339(completed_min)
        if completed_max:
            params['completedMax'] = tc.to_rfc3339(completed_max)
        if include_deleted:
            params['showDeleted'] = include_deleted
        if include_hidden:
            params['showHidden'] = include_hidden

        if task_list == '@default':
            url = Gtasks.TASKS_URL.format(task_list)
        else:
            url = Gtasks.TASKS_URL.format(self.get_list(task_list).id)
        return self._download_items(url, params, Task, self._task_index,
                max_results)

    def get_lists(self, max_results=float('inf')):
        return self._download_items(Gtasks.LISTS_URL, {}, TaskList,
                self._list_index, max_results)

    def get_task(self, task_id, list_id='@default'):
        if task_id in self._task_index:
            task = self._task_index[task_id]
            task.pull_updates()
            return task
        else:
            task_url = Gtasks.TASKS_URL.format(list_id) + task_id
            params = {'task': task_id, 'tasklist': list_id}
            response = self.google.get(task_url, params=params)
            response.raise_for_status()
            return Task(response.json(), self)

    def get_list(self, name_or_id):
        try:
            return self._list_index[name_or_id]
        except KeyError:
            self.get_lists()
            return self._list_index[name_or_id]

    def new_task(self, title='', due_date=None, notes='', complete=False,
            task_list='@default', completion_date=None, parent=None):
        if task_list != '@default':
            task_list = self.get_list(task_list).id
        url = Gtasks.TASKS_URL.format(task_list)
        header = {'content-type': 'application/json'}
        body = {}
        if title:
            body['title'] = title
        if due_date:
            body['due'] = tc.to_date_rfc3339(due_date)
        if notes:
            body['notes'] = notes
        if complete or completion_date:
            body['status'] = 'completed'
        if completion_date:
            body['completed'] = tc.to_rfc3339(completion_date)
        if parent:
            if type(parent) is Task:
                body['parent'] = parent._dict['id']
            elif type(parent) is str:
                body['parent'] = parent
        response = self.google.post(url, data=json.dumps(body), headers=header)
        response.raise_for_status()
        return Task(response.json(), self)

    def new_list(self, title=''):
        header = {'content-type': 'application/json'}
        body = {}
        if title:
            body['title'] = title
        response = self.google.post(Gtasks.LISTS_URL, data=json.dumps(body),
                headers=header)
        response.raise_for_status()
        return TaskList(response.json(), self)
    
    def push_updates(self):
        for task_list in self._list_index.values():
            task_list.push_updates()
            task_list.push_task_updates()

    @contextmanager
    def batch_edit(self):
        old_value = self.auto_push
        self.auto_push = False
        yield
        self.push_updates()
        self.auto_push = old_value
