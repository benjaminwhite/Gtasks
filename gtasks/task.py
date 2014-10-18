import re
import sys
import json

import timeconversion as tc

class Task:
    def __init__(self, title='', complete=False, notes='', due_date=None,
            completion_date=None, updated_date=None, id=None, parent=None,
            position=None, deleted=False, hidden=False, etag=None, self_link=None, 
            gtasks=None):
        # Required
        self._title = title
        self._complete = complete
        self._id = id
        self._position = position
        self._deleted = deleted
        self._hidden = hidden
        self._etag = etag
        self._self_link = self_link
        self._gtasks = gtasks

        if self_link is not None and gtasks is not None:
            list_id = re.search('lists/(\w+)/tasks', self_link).group(1)
            self._task_list = gtasks.get_list(list_id)
        else:
            self._task_list = None

        if updated_date is None or tc.rfc3339_compatible(updated_date):
            self._updated_date = updated_date
        else:
            raise tc.RFC3339ConversionError(updated_date)

        # Optional
        self._notes = notes
        self._parent = parent
        if due_date is None or tc.rfc3339_compatible(due_date):
            self._due_date = due_date
        else:
            raise tc.RFC3339ConversionError(due_date)
        if completion_date is None or tc.rfc3339_compatible(completion_date):
            self._completion_date = completion_date
        else:
            raise tc.RFC3339ConversionError(completion_date)

    @classmethod
    def from_dict(cls, task_dict, gtasks=None):
        task = cls(title=task_dict['title'],
                complete=(task_dict['status'] == 'completed'),
                notes=task_dict.get('notes', None),
                updated_date=tc.from_rfc3339(task_dict['updated']),
                id=task_dict['id'],
                parent=task_dict.get('parent', None),
                position=task_dict['position'],
                deleted=task_dict.get('deleted', False),
                hidden=task_dict.get('hidden', False),
                etag=task_dict['etag'],
                self_link=task_dict['selfLink'])

        if 'due' in task_dict:
            task._due_date = tc.from_rfc3339(task_dict['due'])
        if 'completed' in task_dict:
            task._completion_date = tc.from_rfc3339(task_dict['completed'])

        return task

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        self._title = value
        if self.gtasks.auto_push:
            headers={'Content-Type': 'application/json'}
            params = {'task': self._id, 'tasklist':'@default'}
            body = {'title': self._title}
            r = self.gtasks.google.put(self._self_link, headers=headers, params=params, data=json.dumps(body))
            print(r.text)

    #@property
    #def complete(self):
        #return self._complete
    #@property
    #@property
    #@property
    #@property
    #@property
    #@property
    #@property

    def __unicode__(self):
        mark = u'\u2713' if self._complete else u' ' # u2713 is a checkmark
        return u'({}) {}'.format(mark, self._title)

    def __str__(self):
        if sys.version_info[0] == 2:
            return self.__unicode__().encode('utf-8') # python2's str = bytes
        else:
            return self.__unicode__() # python3's str = unicode

    def __repr__(self):
        return '<Task {}>'.format(self._id)
