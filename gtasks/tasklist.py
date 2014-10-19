from gtaskobject import GtaskObject

class TaskList(GtaskObject):
    def __init__(self, list_dict, gtasks):
        GtaskObject.__init__(self, list_dict, gtasks)

        self.auto_push = gtasks.auto_push
        self.auto_pull = gtasks.auto_pull
        self._task_index = {}

    def push_tasks_updates(self):
        for task in self._task_index:
            task.push_updates()

    def tasks(self, **kwargs):
        return self._google.tasks(self.id, **kwargs)
