class TaskList(object):
    def __init__(self, list_dict, gtasks):
        self._dict = list_dict
        self._gtasks = gtasks
        self._task_index = {}

        self.auto_push = gtasks.auto_push
        self.auto_pull = gtasks.auto_pull

    def tasks(self):
        return self._gtasks.tasks(self.id)
