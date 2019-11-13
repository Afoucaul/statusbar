import os
import subprocess as sp
import threading
import time

from statusbar import utils


class Component(threading.Thread):
    def __init__(self, fmt, delay=1):
        super().__init__()

        self._delay = delay
        self._fmt = fmt

        self._status = ""
        self._status_lock = threading.Lock()

    def fetch(self):
        raise NotImplementedError

    def run(self):
        try:
            while True:
                self.status = self._fmt.format(**self.fetch())
                time.sleep(self._delay)
        except Exception as error:
            print(error)
            self.status = type(error).__name__

    @property
    def status(self) -> str:
        with self._status_lock:
            return self._status

    @status.setter
    def status(self, value: str):
        with self._status_lock:
            self._status = value


class Battery(Component):
    BATTERY_STATUS = {
        'full': 'F',
        'charging': '>',
        'discharging': '<'
    }

    def __init__(self, delay, index, fmt):
        super().__init__(fmt, delay)
        self.index = index

    def fetch(self):
        base = f"/sys/class/power_supply/BAT{self.index}"
        present = False
        with open(os.path.join(base, 'present'), 'r') as fd:
            content = fd.read()
            present = content.strip() == '1'

        energy_max = 0
        with open(os.path.join(base, 'energy_full_design'), 'r') as fd:
            content = fd.read()
            energy_max = float(content)

        energy_remaining = 0
        with open(os.path.join(base, 'energy_now'), 'r') as fd:
            content = fd.read()
            energy_remaining = float(content)

        status = ""
        with open(os.path.join(base, 'status'), 'r') as fd:
            content = fd.read()
            status = content.strip().lower()

        if status == 'full':
            energy = 1
        else:
            energy = energy_remaining / energy_max

        energy_gauge = utils.make_gauge_image(energy)
        status = self.BATTERY_STATUS.get(status, '?')
        return {'energy': energy_gauge, 'status': status}


class Volume(Component):
    def fetch(self):
        ps = sp.Popen(
            """pactl list sinks | grep -oP "(?<=Volume:.)*\d+(?=%)" | head -1""",
            shell=True,
            stdout=sp.PIPE
        )
        return {'volume': int(ps.communicate()[0]) / 100}
