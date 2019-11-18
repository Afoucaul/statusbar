import threading
import time


class StatusBar(threading.Thread):
    def __init__(self, fmt: str, components: dict, callback, delay: int=None):
        super().__init__()
        self.fmt = fmt
        self.components = components
        self.callback = callback
        if delay is not None:
            self.delay = delay
        else:
            self.delay = min(x.delay for x in components.values())

    def start(self):
        for component in self.components.values():
            component.start()

        super().start()

    def run(self):
        while True:
            status = self.fmt.format(**{
                name: component.status
                for name, component in self.components.items()
            })
            self.callback(status)
            time.sleep(self.delay)
