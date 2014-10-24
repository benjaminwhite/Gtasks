import re
import sys

from gtaskobject import GtaskObject
from tasklist import TaskList
from timeconversion import to_rfc3339, from_rfc3339 
from misc import raise_for_type

class Task(GtaskObject):
    LIST_REGEX = re.compile('lists/(\w+)/tasks')

    def __init__(self, task_dict, gtasks):
        GtaskObject.__init__(self, task_dict, gtasks)

        list_id = Task.LIST_REGEX.search(task_dict['selfLink']).group(1)
        if list_id in gtasks._list_index:
            self.task_list = gtasks._list_index[list_id]
        else:
            self.task_list = TaskList({'id': list_id}, gtasks)

        task_id = task_dict['id']
        self.task_list._task_index[task_id] = self
        gtasks._task_index[task_id] = self

        self._parent_settings = self.task_list
        self._update_params = {'tasklist': list_id, 'task': task_id}

    # hidden property (read-only)
    @property
    def hidden(self):
        return self._get_property('hidden')

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
            date = from_rfc3339(date)
        return date

    @due_date.setter
    def due_date(self, value):
        self._set_property('due', to_rfc3339(value))

    # completion_date property
    @property
    def completion_date(self):
        date = self._get_property('completed')
        if date is not None:
            date = from_rfc3339(date)
        return date

    @completion_date.setter
    def completion_date(self, value):
        self._set_property('completed', to_rfc3339(value))

    # deleted property
    @property
    def deleted(self):
        return self._get_property('deleted')

    @deleted.setter
    def deleted(self, value):
        self._set_property('deleted', value, bool)

    def __unicode__(self):
        mark = u'\u2713' if self.complete else u' ' # u2713 is a checkmark
        return u'({}) {}'.format(mark, self.title)
