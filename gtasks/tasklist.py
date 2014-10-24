from gtaskobject import GtaskObject

class TaskList(GtaskObject):
    def __init__(self, list_dict, gtasks):
        GtaskObject.__init__(self, list_dict, gtasks)
        gtasks._list_index[self.id] = self
        if 'title' in list_dict:
            gtasks._list_index[list_dict['title']] = self
        self._task_index = {}

    def push_tasks_updates(self):
        for task in self._task_index:
            task.push_updates()

    def pull_tasks_updates(self):
        self.tasks()

    def tasks(self, **kwargs):
        return self._google.tasks(self.id, **kwargs)

    def __iter__(self):
        return self.tasks(self.id)
