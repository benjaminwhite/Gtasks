from __future__ import absolute_import

import json
from contextlib import contextmanager

import gtasks.timeconversion as tc
from gtasks.misc import unicode_to_str, raise_for_type

class GtaskObject(object):
    def __init__(self, item_dict, gtasks):
        self._dict = item_dict
        self._gtasks = gtasks

        self._auto_push = None
        self._auto_pull = None
        self._parent_settings = gtasks

        self._update_headers = {'content-type': 'application/json'}
        self._update_params = {}
        self._update_body = {}

    def push_updates(self):
        if self._update_body:
            response = self._gtasks.google.patch(self._dict['selfLink'],
                    headers=self._update_headers, params=self._update_params,
                    data=json.dumps(self._update_body))
            response.raise_for_status()
            self._dict = response.json()
            self._update_body.clear()

    def pull_updates(self):
        response = self._gtasks.google.get(self._dict['selfLink'])
        response.raise_for_status()
        self._dict = response.json()

    def _get_property(self, key, pull_override=None):
        if (self.auto_pull and pull_override is None) or pull_override:
            self.pull_updates()
        return self._dict.get(key, None)

    def _set_property(self, key, value, expected_type=None, push_override=None):
        if expected_type:
            raise_for_type(value, expected_type)

        self._update_body[key] = value
        if (self.auto_push and push_override is None) or push_override:
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

    @contextmanager
    def batch_edit(self):
        old_value = self._auto_push
        self._auto_push = False
        yield
        self.push_updates()
        self._auto_push = old_value

    # id property (read-only)
    @property
    def id(self):
        return self._get_property('id', pull_override=False)

    # updated_date property (read-only)
    @property
    def updated_date(self):
        date = self._get_property('updated')
        if date is not None:
            date = tc.from_rfc3339(date)
        return date

    # title property
    @property
    def title(self):
        return self._get_property('title')

    @title.setter
    def title(self, value):
        self._set_property('title', value, str)

    def __hash__(self):
        return self._dict['id']

    def __unicode__(self):
        return u'{}'.format(self.title)

    def __str__(self):
        return unicode_to_str(self.__unicode__())

    def __repr__(self):
        short_title = unicode_to_str(self.title)
        obj_id = unicode_to_str(self._dict['id'])
        if short_title and len(short_title) > 30:
            short_title = '{}...'.format(short_title[:27])
        return '<{} "{}":{}>'.format(self.__class__.__name__, short_title, obj_id)
