import statusbar
from statusbar import components
from statusbar import bar as statusbar

fmt = " " + " | ".join((
    "{bat0}",
    "{bat1}",
    "{vol}",
    "{wifi}",
)) + " "
components = {
    'bat0': components.Battery("M:[{energy}]{status}", 0),
    'bat1': components.Battery("S:[{energy}]{status}", 1),
    'vol': components.Volume("vol: {volume:.0%}"),
    'wifi': components.WiFi("{essid}: {power}", "wlp3s0"),
}

bar = statusbar.StatusBar(fmt, components, print)
bar.start()
