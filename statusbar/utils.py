WIDTH_BLOCKS = " ▏▎▍▌▋▊▉█"
STAIR_BLOCKS = "▂▄▆█"


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
