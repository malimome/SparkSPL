'''
Created on Apr 05, 2015
@author: Mohsen Alimomeni
'''

import threading
import sys


class ResultCatcher:
    def __init__(self, f):
        self.f = f
        self.val = None

    def __call__(self, *args, **kwargs):
        self.exc_info = None
        try:
            self.val = self.f(*args, **kwargs)
        except Exception:
            self.exc_info = sys.exc_info()


def threaded(f):
    def decorator(*args, **kargs):
        # Encapsulate f so that the return value can be extracted.
        ret = ResultCatcher(f)

        th = threading.Thread(target=ret, args=args)
        th.start()
        # Extract and return the result of executing f.
        return th, ret

    decorator.__name__ = f.__name__
    return decorator