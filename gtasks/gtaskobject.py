class GtaskObject(object):
    def __init__(self, item_dict, gtasks):
        self._dict = item_dict
        self._gtasks = gtasks

        self._auto_push = None
        self._auto_pull = None
        self._parent_settings = gtasks

        self._update_params = {}
        self._update_body = {}

    def push_updates(self):
        if self._update_body:
            response = self._gtasks.session.put(self._dict['selfLink'],
                    params=self._update_params, data=self._update_body)
            response.raise_for_status()
            self._dict.update(response.json())
            self._update_body.clear()

    def pull_updates(self):
        response = self._gtasks.session.get(self._dict['selfLink'])
        response.raise_for_status()
        self._dict = response.json()

    def _get_property(self, key):
        if self.auto_pull:
            self.pull_updates()
        return self._dict.get(key, None)

    def _set_property(self, key, value, expected_type=None):
        if expected_type:
            raise_for_type(value, expected_type)

        self._update_body[key] = value
        if self.auto_push:
            self.push_updates()
        else:
            self._dict[key] = value

    # auto_push property
    @property
    def auto_push(self):
        if self._auto_push is None:
            return self._parent_settings.auto_push
        else:
            return self._auto_push

    @auto_push.setter
    def auto_push(self, value):
        raise_for_type(value, bool)
        self._auto_push = value

    # auto_pull property
    @property
    def auto_pull(self):
        if self._auto_pull is None:
            return self._parent_settings.auto_pull
        else:
            return self._auto_pull

    @auto_pull.setter
    def auto_pull(self, value):
        raise_for_type(value, bool)
        self._auto_pull = value

    # id property (read-only)
    @property
    def id(self):
        return self._get_property('id')

    # title property
    @property
    def title(self):
        return self._get_property('title')

    @title.setter
    def title(self, value):
        self._set_property('title', value, str)

    def __repr__(self):
        return '<GoogleObject {}>'.format(self.id)

def raise_for_type(value, expected_type):
    if expected_type and type(value) is not expected_type:
        raise ValueError('{} is not of type: {}'.format(value, expected_type))
