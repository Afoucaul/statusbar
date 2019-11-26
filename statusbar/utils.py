import subprocess as sp


WIDTH_BLOCKS = " ▏▎▍▌▋▊▉█"
STAIR_BLOCKS = "▂▄▆█"
GRAPH_BLOCKS = "▁▂▃▄▅▆▇█"


def make_gauge_image(percentage, *, width=8):
    if percentage == 1:
        return WIDTH_BLOCKS[-1] * width

    eighths = 8 * width
    full, rem = divmod(percentage * eighths, 8)
    image = WIDTH_BLOCKS[-1] * int(full) + WIDTH_BLOCKS[int(rem)]
    image += " " * (width - len(image))

    return image


def make_stair_image(percentage):
    blocks = round(percentage * len(STAIR_BLOCKS))
    return (
        STAIR_BLOCKS[:blocks]
        + " " * (len(STAIR_BLOCKS) - blocks)
    )


def xsetroot_name(name):
    return sp.run(['xsetroot', '-name', name])


def make_graph_image(percentages):
    return "".join(map(
        lambda x: GRAPH_BLOCKS[min(len(GRAPH_BLOCKS) - 1, int(x * len(GRAPH_BLOCKS)))],
        percentages
    ))
