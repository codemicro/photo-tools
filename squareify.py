import sys
from PIL import Image

BORDER_PADDING = 0
IMAGE_FILE = sys.argv[1]

im = Image.open(IMAGE_FILE)

og_w, og_h = im.size
target_dimension = max([og_w, og_h]) + BORDER_PADDING

w_pos = int((target_dimension - og_w) / 2)
h_pos = int((target_dimension - og_h) / 2)

result = Image.new(im.mode, (target_dimension, target_dimension), (255, 255, 255))
result.paste(im, (w_pos, h_pos))

sp = IMAGE_FILE.split(".")
file_ext = sp[-1]

output_file = ".".join(sp[:-1] + ["square", file_ext])
result.save(output_file, quality=97)