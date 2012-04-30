# -*- coding: utf-8 -*-
from collections import defaultdict


# TODO: Use tree() to simplify identify_to_dict
def tree():
    '''Recursive Tree data-sctructure based on defaultdict'''
    return defaultdict(tree)


def tree_to_dict(t):
    '''Tree tree() -> nested dicts'''
    return {k: dicts(t[k]) for k in t}


def tree_add(t, keys):
    '''Adds a list of keys to tree()'''
    for key in keys:
        t = t[key]


class CaseInsensitiveDict(dict):
    """Case-insensitive Dictionary for headers. From httpbin

    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header.
    """

    def _lower_keys(self):
        return map(str.lower, self.keys())

    def __contains__(self, key):
        return key.lower() in self._lower_keys()

    def __getitem__(self, key):
        # We allow fall-through here, so values default to None
        if key in self:
            return self.items()[self._lower_keys().index(key.lower())][1]
