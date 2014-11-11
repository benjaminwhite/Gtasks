from __future__ import absolute_import

import re
from contextlib import contextmanager

import gtasks.timeconversion as tc
from gtasks.gtaskobject import GtaskObject
from gtasks.misc import raise_for_type
from gtasks.tasklist import TaskList

class Task(GtaskObject):
    LIST_REGEX = re.compile('lists/(\w+)/tasks')

    def __init__(self, task_dict, gtasks):
        GtaskObject.__init__(self, task_dict, gtasks)

        list_id = Task.LIST_REGEX.search(task_dict['selfLink']).group(1)
        if list_id in gtasks._list_index:
            self.task_list = gtasks._list_index[list_id]
        else:
            list_dict = {'id': list_id, 'selfLink': gtasks.LISTS_URL+'/'+list_id}
            self.task_list = TaskList(list_dict, gtasks)

        task_id = task_dict['id']
        self.task_list._task_index[task_id] = self
        gtasks._task_index[task_id] = self

        self._parent_settings = self.task_list
        self._update_params = {'task': task_id, 'tasklist': list_id}

    def unhide(self):
        self._set_property('hidden', False)

    @contextmanager
    def batch_edit(self):
        old_value = self._auto_push
        self._auto_push = False
        yield
        self.push_updates()
        self._auto_push = old_value

    # hidden property (read-only)
    @property
    def hidden(self):
        return self._get_property('hidden') is True

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
        raise_for_type(value, bool)
        if value:
            self._set_property('status', 'completed')
        else:
            self._set_property('completed', None, push_override=False)
            self._set_property('status', 'needsAction')

    # due_date property
    @property
    def due_date(self):
        date = self._get_property('due')
        if date is not None:
            date = tc.from_date_rfc3339(date)
        return date

    @due_date.setter
    def due_date(self, value):
        if value is None:
            self._set_property('due', None)
        else:
            self._set_property('due', tc.to_date_rfc3339(value))

    # completion_date property
    @property
    def completion_date(self):
        date = self._get_property('completed')
        if date is not None:
            date = tc.from_rfc3339(date)
        return date

    @completion_date.setter
    def completion_date(self, value):
        if value is None:
            self._set_property('status', 'needsAction', push_override=False)
            self._set_property('completed', None)
        else:
            self._set_property('status', 'completed', push_override=False)
            self._set_property('completed', tc.to_rfc3339(value))

    # deleted property
    @property
    def deleted(self):
        return self._get_property('deleted') is True

    @deleted.setter
    def deleted(self, value):
        self._set_property('deleted', value, bool)

    # parent proprty
    @property
    def parent(self):
        parent_id = self._get_property('parent')
        if parent_id:
            return self._gtasks.get_task(parent_id)
        else:
            return None

    def __unicode__(self):
        mark = u'\u2713' if self.complete else u' ' # u2713 is a checkmark
        return u'({}) {}'.format(mark, self.title)
