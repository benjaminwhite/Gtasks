import re
import sys

from gtaskobject import GtaskObject, raise_for_type
from tasklist import TaskList

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
            self._set_property('status', 'needsAction')

    # deleted property
    @property
    def deleted(self):
        return self._get_property('deleted')

    @deleted.setter
    def deleted(self, value):
        self._set_property('notes', value, bool)

    # Python2's Unicode Magic Method
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
