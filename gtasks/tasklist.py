from __future__ import absolute_import

from contextlib import contextmanager

from gtasks.gtaskobject import GtaskObject

class TaskList(GtaskObject):
    CLEAR_URL = 'https://www.googleapis.com/tasks/v1/lists/{}/clear'

    def __init__(self, list_dict, gtasks):
        GtaskObject.__init__(self, list_dict, gtasks)

        gtasks._list_index[list_dict['id']] = self
        if 'title' in list_dict:
            gtasks._list_index[list_dict['title']] = self
        self._task_index = {}

    def get_tasks(self, include_completed=True, due_min=None, due_max=None,
            max_results=float('inf'), updated_min=None, completed_min=None,
            completed_max=None, include_deleted=False, include_hidden=False):
        return self._gtasks.get_tasks(include_completed, due_min, due_max,
            self._dict['id'], max_results, updated_min, completed_min,
            completed_max, include_deleted, include_hidden)

    def get_task(self, task_id):
        return self._gtasks.get_task(task_id, self._dict['id'])

    def new_task(self, title='', due_date=None, notes='', complete=False,
            completion_date=None, parent=None):
        return self._gtasks.new_task(title, due_date, notes, complete,
                self._dict['id'], completion_date, parent)

    def push_task_updates(self):
        for task in self._task_index.values():
            task.push_updates()

    def pull_task_updates(self):
        self.get_tasks() # TODO: need smarter pull's involving update_min

    def clear(self):
        url = TaskList.CLEAR_URL.format(self._dict['id'])
        response = self._gtasks.google.post(url)
        response.raise_for_status()

    def unclear(self):
        for task in self.get_tasks(include_hidden=True):
            if task.hidden:
                task.unhide()

    def permanently_delete(self):
        response = self._gtasks.google.delete(self._dict['selfLink'])
        response.raise_for_status()
        title = self._dict['title']
        for task in self._task_index:
            del self._gtasks._task_index[task._dict['id']]
            task._dict['deleted'] = 'True'
        self._task_index.clear()
        del self._gtasks._list_index[self._dict['id']]
        try:
            del self._gtasks._list_index[title]
            for other_list in self._gtasks._list_index.values():
                if other_list._dict['title'] == title:
                    self._gtasks._list_index[title] = other_list
                    break
        except Exception:
            pass

    @contextmanager
    def batch_edit(self):
        old_value = self._auto_push
        self._auto_push = False
        yield
        self.push_updates()
        self.push_task_updates()
        self._auto_push = old_value

    # title property
    @property
    def title(self):
        pull_override = 'title' not in self._dict
        return self._get_property('title', pull_override)

    def __iter__(self):
        return iter(self.get_tasks())

    def __len__(self):
        return len(self.get_tasks())
