import threading


class LockedIterator(object):
    def __init__(self, it):
        self.lock = threading.Lock()
        self.it = iter(it)

    def __iter__(self):
        return self

    def __next__(self):
        self.lock.acquire()
        try:
            item = next(self.it)
            return item
        except StopIteration:
            return None
        finally:
            self.lock.release()
