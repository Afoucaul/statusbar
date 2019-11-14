from statusbar import bar as statusbar
from statusbar import components
from statusbar import utils
from statusbar import weathercli


fmt = " " + " | ".join((
    "{bat0}",
    "{bat1}",
    "{vol}",
    "{wifi}",
    "{weather}",
    "{datetime}",
)) + " "

session = weathercli.Session.from_env()
components = {
    'bat0': components.Battery("M:[{energy}]{status}", 0),
    'bat1': components.Battery("S:[{energy}]{status}", 1),
    'vol': components.Volume("vol: {volume:.0%}"),
    'wifi': components.WiFi("{essid}: {power}", "wlp3s0"),
    'datetime': components.DateTime("{date} - {time}"),
    'weather': components.Weather("{city} - {temp}°, {condition}", session),
}

bar = statusbar.StatusBar(fmt, components, utils.xsetroot_name)
bar.start()
