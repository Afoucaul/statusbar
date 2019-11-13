import statusbar
from statusbar import components
from statusbar import bar as statusbar

fmt = " " + " | ".join((
    "{bat0}",
    "{bat1}",
    "{vol}"
)) + " "
components = {
    'bat0': components.Battery(1, 0, "M:[{energy}]{status}"),
    'bat1': components.Battery(1, 1, "M:[{energy}]{status}"),
    'vol': components.Volume("vol: {volume:.0%}")
}

bar = statusbar.StatusBar(fmt, components, print)
bar.start()
