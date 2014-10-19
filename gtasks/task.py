import re
import sys

import timeconversion as tc

from tasklist import TaskList

class Task(object):
    LIST_REGEX = re.compile('lists/(\w+)/tasks')

    def __init__(self, task_dict, gtasks):
        self._dict = task_dict
        self._gtasks = gtasks

        list_id = Task.LIST_REGEX.search(task_dict['selfLink']).group(1)
        if list_id in gtasks._list_index:
            self.task_list = gtasks._list_index[list_id]
        else:
            self.task_list = TaskList({'id': list_id}, gtasks)

        task_id = task_dict['id']
        self.task_list._task_index[task_id] = self
        gtasks._task_index[task_id] = self

        self.auto_push = self.task_list.auto_push
        self.auto_pull = self.task_list.auto_pull

        self._update_params = {'tasklist': list_id, 'task': task_id}
        self._update_body = {}

    def push_updates(self):
        if self._update_body:
            response = self._gtasks.google.put(self._dict['selfLink'],
                    params=self._update_params, data=self._update_body) # may need to convert to json
            response.raise_for_status()
            self._dict.update(response.json())
            self._update_body.clear()

    def pull_updates(self):
        response = self._gtasks.google.get(self._dict['selfLink'])
        response.raise_for_status()
        self._dict = response.json()

    def _get_property(self, key):
        if self.auto_pull:
            self.pull_updates()
        return self._dict.get(key, None)

    def _set_property(self, key, value, expected_type):
        if type(value) is not expected_type:
            raise ValueError('{} is not of type: {}'.format(value, expected_type))
        self._update_body[key] = value
        if self.auto_push:
            self.push_updates()
        else:
            self._dict[key] = value

    # id property (read-only)
    @property
    def id(self):
        return self._get_property('id')

    # hidden property (read-only)
    @property
    def hidden(self):
        return self._get_property('hidden')

    # title property
    @property
    def title(self):
        return self._get_property('title')
    @title.setter
    def title(self, value):
        self._set_property('title', value, str)

    # notes property
    @property
    def notes(self):
        return self._get_property('notes')
    @notes.setter
    def notes(self, value):
        self._set_property('notes', value, str)

    # complete property
    @property
    def complete(self):
        return self._get_property('status') == 'completed'
    @complete.setter
    def complete(self, value):
        if type(value) is not bool:
            raise ValueError('{} is not of type: {}'.format(value, bool))
        if value:
            self._set_property('status', 'completed', str)
        else:
            self._set_property('status', 'needsAction', str)

    # deleted property
    @property
    def deleted(self):
        return self._get_property('deleted')
    @deleted.setter
    def deleted(self, value):
        self._set_property('notes', value, bool)

    def __unicode__(self):
        mark = u'\u2713' if self.complete else u' ' # u2713 is a checkmark
        return u'({}) {}'.format(mark, self.title)

    def __str__(self):
        if sys.version_info[0] == 2:
            return self.__unicode__().encode('utf-8') # python2's str = bytes
        else:
            return self.__unicode__() # python3's str = unicode

    def __repr__(self):
        return '<Task {}>'.format(self.id)
