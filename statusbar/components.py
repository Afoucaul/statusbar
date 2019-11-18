import datetime as dt
import os
import re
import subprocess as sp
import threading
import time

from statusbar import utils
from statusbar import weathercli


class Component(threading.Thread):
    def __init__(self, fmt: str, *, delay: float=1):
        super().__init__()

        self._delay = delay
        self.fmt = fmt

        self._status = ""
        self._status_lock = threading.Lock()

    def fetch(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        try:
            while True:
                self.fetch()
                time.sleep(self._delay)
        except Exception as error:
            print(error)
            self.status = type(error).__name__
            raise

    @property
    def delay(self) -> float:
        return self._delay

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

    def __init__(self, fmt, path, *, delay=1):
        super().__init__(fmt, delay=delay)
        self.path = path

    def fetch(self):
        present = False
        with open(os.path.join(self.path, 'present'), 'r') as fd:
            content = fd.read()
            present = content.strip() == '1'

        energy_max = 0
        with open(os.path.join(self.path, 'energy_full_design'), 'r') as fd:
            content = fd.read()
            energy_max = float(content)

        energy_remaining = 0
        with open(os.path.join(self.path, 'energy_now'), 'r') as fd:
            content = fd.read()
            energy_remaining = float(content)

        status = ""
        with open(os.path.join(self.path, 'status'), 'r') as fd:
            content = fd.read()
            status = content.strip().lower()

        if status == 'full':
            energy = 1
        else:
            energy = energy_remaining / energy_max

        energy_gauge = utils.make_gauge_image(energy)
        status = self.BATTERY_STATUS.get(status, '?')
        self.status = self.fmt.format(energy=energy_gauge, status=status)


class Volume(Component):
    def fetch(self):
        ps = sp.Popen(
            """pactl list sinks | grep -oP "(?<=Volume:.)*\d+(?=%)" | head -1""",
            shell=True,
            stdout=sp.PIPE
        )
        self.status = self.fmt.format(volume=int(ps.communicate()[0]) / 100)


class WiFi(Component):
    WIFI_REGEX = re.compile(
        r'ESSID:"(?P<essid>.*?)".*'
        r'Link Quality=(?P<power>\d+)/(?P<max_power>\d+)',
        re.MULTILINE + re.DOTALL
    )

    def __init__(self, fmt, interface, *, delay=1):
        super().__init__(fmt, delay=delay)
        self.interface = interface

    def fetch(self):
        output = sp.getoutput(['iwconfig', self.interface])
        match = self.WIFI_REGEX.search(output)

        if match:
            essid = match.group('essid')
            power = float(match.group('power')) / float(match.group('max_power'))
            power_image = utils.make_stair_image(power)
            self.status = self.fmt.format(essid=essid, power=power_image)

        else:
            self.status = "No WiFi"


class DateTime(Component):
    def __init__(self, fmt):
        super().__init__(fmt, delay=0.5)

    def fetch(self):
        now = dt.datetime.now()
        date = now.strftime("%d/%m/%y")
        if now.microsecond // 500_000 == 0:
            time = now.strftime("%H:%M")
        else:
            time = now.strftime("%H %M")

        self.status = self.fmt.format(date=date, time=time)


class Weather(Component):
    def __init__(self, fmt, cli, *, delay=3600):
        super().__init__(fmt, delay=delay)
        self.cli = cli

    def fetch(self):
        current_coordinates = None
        while current_coordinates is None:
            current_coordinates = weathercli.current_coordinates()
            if current_coordinates is None:
                self.status = "Fetching coordinates..."
                time.sleep(10)

        success = False
        while not success:
            response = self.cli.weather(**current_coordinates)
            success = response.status_code == 200

            if not success:
                self.status = "Fetching weather..."
                time.sleep(10)
                continue

            info = response.json()
            self.status = self.fmt.format(
                city=info['name'],
                temp=info['main']['temp'],
                condition=info['weather'][0]['main']
            )
