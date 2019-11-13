import threading
import time


class Component(threading.Thread):
    def __init__(self, delay):
        super().__init__()

        self._delay = delay
        self._status = ""
        self._status_lock = threading.Lock()

    def fetch(self):
        raise NotImplementedError

    def run(self):
        while True:
            self.status = self.fetch()
            time.sleep(self.delay)

    @property
    def status(self) -> str:
        with self._status_lock:
            return self._status

    @status.set
    def status(self, value: str):
        with self._status_lock:
            self._status = value
