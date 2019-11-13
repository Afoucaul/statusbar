WIDTH_BLOCKS = " ▏▎▍▌▋▊▉█"


def make_gauge_image(percentage, *, width=8):
    if percentage == 1:
        return WIDTH_BLOCKS[-1] * width

    eighths = 8 * width
    full, rem = divmod(percentage * eighths, 8)
    image = WIDTH_BLOCKS[-1] * int(full) + WIDTH_BLOCKS[int(rem)]
    image += " " * (width - len(image))

    return image
