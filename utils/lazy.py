# -*- coding: utf-8 -*-

from functools import partial

class LazyList(object):
    def __init__(self, fn, *args, **kwargs):
        super(LazyList, self).__init__()
        self.fn = partial(fn, *args, **kwargs)
        self._L = None

    @property
    def L(self):
        if self._L is None:
            import traceback; traceback.print_stack()
            self._L = list(self.fn())
        return self._L

    def __len__(self):
        return len(self.L)

    def __getitem__(self, index):
        return self.L[index]

    def __setitem__(self, index, value):
        self.L[index] = value

    def __delitem__(self, index):
        del self.L[index]
