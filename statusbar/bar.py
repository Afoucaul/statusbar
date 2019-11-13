from statusbar import component


class StatusBar(object):
    def __init__(self, fmt: str, components: dict):
        self.fmt = fmt
        self.components = components

    def __str__(self):
        status = {
            name: component.status
            for name, component in components.items()
        }
        return self.fmt.format(**status)
