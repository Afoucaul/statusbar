from statusbar import bar as statusbar
from statusbar import components
from statusbar import utils
from statusbar import weathercli


def main():
    fmt = " " + " | ".join((
        "{bat0}",
        "{bat1}",
        "{vol}",
        "{wifi}",
        "{weather}",
        "{datetime}",
    )) + " "

    session = weathercli.Session.from_env()
    parts = {
        'bat0': components.DwmBattery(
            "M:[{energy}]{status}",
            "/sys/class/power_supply/BAT0"
        ),
        'bat1': components.DwmBattery(
            "S:[{energy}]{status}",
            "/sys/class/power_supply/BAT1"
        ),
        'vol': components.Volume("vol: {volume:.0%}"),
        'wifi': components.WiFi("{essid}: {power}", "wlp3s0"),
        'datetime': components.DateTime("{date} - {time}"),
        'weather': components.Weather("{city} - {temp}°, {condition}", session),
    }

    bar = statusbar.StatusBar(fmt, parts, utils.xsetroot_name)
    bar.start()


if __name__ == '__main__':
    main()
