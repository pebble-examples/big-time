#!/bin/env python
#
# Used to create image tiles suitable for use by the "Big Watch" watch
# face.
#
# The meta data for the images produced is output to the terminal for
# copy pasta into `resource_map.json`.
#
#
# This script should be run from the root of the watch project
# directory, like this:
#
#    python fonttools/font2png.py
#
# On Mac OS X you can use it like this to have the meta data copied
# directly to the clipboard, ready for pasting:
#
#     python fonttools/font2png.py | pbcopy
#
#
# These image tiles are needed because Pebble can't handle the 100
# point font size required by the watch. Each image tile is a quarter
# of the display.
#
# The generation of tiles is more complicated than it needs to be due to:
#
#   a) For Nevis (at least) the digits seem to return a fixed height
#      of 115 pixels even though the digits don't take up that much
#      vertical space. This means we can't use `getsize()` for
#      dimensions.
#
#   b) The bottom of the digits seem to get clipped (by PIL) unless
#      the canvas has a bunch of extra space. (This may be related to
#      <http://stackoverflow.com/questions/1933766/fonts-clipping-with-pil>
#      or
#      <http://stackoverflow.com/questions/13821882/pil-cut-off-letters/13831117#13831117>.)
#
# Because of these complications, we have to center the digit
# manually.
#
# We first plot the digit on a large canvas, then crop to just the
# bounds of the character and then paste the result centered on a
# canvas of the correct size.
#

import sys

from PIL import ImageFont, ImageDraw, Image

DEFAULT_FONT_FILE_PATH = "resources/fonts/nevis.ttf"

META_DATA_TEMPLATE = \
"""
        {
        "type": "bitmap",
        "defName": "IMAGE_NUM_%d",
        "file": "images/num_%d.png"
        }"""


def gen_bitmaps(font_file_path=DEFAULT_FONT_FILE_PATH):
    # generate meta data
    meta_data_entries = []
    for digit in range(0, 10):
        meta_data_entries.append(META_DATA_TEMPLATE % (digit, digit))

    RESOURCES_TO_GENERATE = [
        (
            # 140w - 72x84 pixels (i.e. a quarter of the Aplite/Basalt display)
            "resources/images/num_%d~rect~144w.png",
            144 / 2,
            168 / 2,
            100,
            100,
            100
        ),
        (
            # 180w - 64x75 pixels
            "resources/images/num_%d~round~180w.png",
            64,
            75,
            100,
            100,
            100
        ),
        (
            # 200w - 100x114 pixels
            "resources/images/num_%d~rect~200w.png",
            200 / 2,
            228 / 2,
            140,
            140,
            140
        )
    ]

    for output_image_filepath_template, tile_width_pixels, tile_height_pixels, font_size, scratch_width_pixels, scratch_height_pixels in RESOURCES_TO_GENERATE:
        font = ImageFont.truetype(font_file_path, font_size)
        final_tile_canvas_dimensions = (tile_width_pixels, tile_height_pixels)
        scratch_canvas_dimensions = (scratch_width_pixels, scratch_height_pixels)
        # Generate the image tile file for each digit.
        for digit in range(0, 10):
            # Draw the digit on a large canvas so PIL doesn't crop it.
            scratch_canvas_image = Image.new("RGB", scratch_canvas_dimensions)
            draw = ImageDraw.Draw(scratch_canvas_image)

            draw.text((0,0), str(digit), font=font)

            # Discard all the padding
            cropped_digit_image = scratch_canvas_image.crop(scratch_canvas_image.getbbox())

            # Center the digit within the final image tile and save it
            digit_width, digit_height = cropped_digit_image.size

            tile_image = Image.new("RGB", final_tile_canvas_dimensions)

            tile_image.paste(cropped_digit_image, ((tile_width_pixels-digit_width)/2, (tile_height_pixels-digit_height)/2))

            tile_image.save(output_image_filepath_template % digit)


    # Display the meta data which needs to be included in `resource_map.json`.
    print ",\n".join(meta_data_entries)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    gen_bitmaps()

    return 0


if __name__ == "__main__":
    sys.exit(main())
