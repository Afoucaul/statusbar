import datetime as dt
import os
import psutil
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

    def update_status(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        try:
            while True:
                self.update_status()
                time.sleep(self._delay)

        except Exception as error:
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

        return status, energy

    def update_status(self):
        status, energy = self.fetch()

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
        volume = int(ps.communicate()[0]) / 100

        return volume

    def update_status(self):
        volume = self.fetch()
        self.status = self.fmt.format(volume=volume)


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
            return essid, float(match.group('power')) / float(match.group('max_power'))

        else:
            return None

    def update_status(self):
        result = self.fetch()
        if result is not None:
            essid, power = result
            power_image = utils.make_stair_image(power)
            self.status = self.fmt.format(essid=essid, power=power_image)
        else:
            self.status = "No WiFi"


class DateTime(Component):
    def __init__(self, fmt, *, blink=True):
        if blink:
            delay = 0.5
            self.fetch = self.fetch_blink
        else:
            delay = 1
            self.fetch = self.fetch_no_blink

        super().__init__(fmt, delay=delay)

    def fetch_no_blink(self):
        now = dt.datetime.now()
        date = now.strftime("%d/%m/%y")
        time = now.strftime("%H:%M")

        return date, time

    def fetch_blink(self):
        now = dt.datetime.now()
        date = now.strftime("%d/%m/%y")
        if now.microsecond // 500_000 == 0:
            time = now.strftime("%H:%M")
        else:
            time = now.strftime("%H %M")

        return date, time

    def update_status(self):
        date, time = self.fetch()
        self.status = self.fmt.format(date=date, time=time)


class Weather(Component):
    def __init__(self, fmt, cli, *, delay=3600):
        super().__init__(fmt, delay=delay)
        self.cli = cli

    def update_status(self):
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
                temp=round(float(info['main']['temp'])),
                condition=info['weather'][0]['main']
            )


class DwmBattery(Battery):
    def update_status(self):
        status, energy = self.fetch()

        energy_gauge = utils.make_gauge_image(energy)
        color = ""
        if status not in ("charging", "full"):
            if energy <= 0.1:
                color = "\x04"
            elif energy <= 0.3:
                color = "\x03"

        elif status == 'charging':
            color = "\x02"

        status = self.BATTERY_STATUS.get(status, '?')
        self.status = color + self.fmt.format(energy=energy_gauge, status=status) + "\x01"


class CpuUsage(Component):
    def __init__(self, fmt, *, delay=5, window_size=5):
        super().__init__(fmt, delay=delay)
        self.values = [0] * window_size

    def fetch(self):
        return psutil.cpu_percent() / 100

    def update_status(self):
        new_value = self.fetch()
        self.values.pop(0)
        self.values.append(new_value)

        graph_image = utils.make_graph_image(self.values)
        self.status = self.fmt.format(cpu=graph_image)
