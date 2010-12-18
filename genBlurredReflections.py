import os
import re
from PIL import Image, ImageOps
import scipy
from math import *

extsize = 24


for fname in os.listdir('input/code/'):
	match = re.match(r"(\w+)Thumb\.jpg", fname)
	if match:
		im = Image.open("input/code/"+fname)
		im = ImageOps.flip(im)

		w, h = im.size

		im2 = Image.new("RGBA", (im.size[0] + extsize*2, int(im.size[1] * 0.7)))

		def blur(im, xy, radius, samples, alpha):
			xcoords = [c*radius for c in scipy.random.standard_normal((samples))]
			ycoords = [c*radius for c in scipy.random.standard_normal((samples))]

			color = [0.0, 0.0, 0.0]
			psamples = 0

			for xoff, yoff in zip(xcoords, ycoords):
				x = int(xy[0]+xoff)
				y = int(xy[1]+yoff)
				if x >= 0 and x < im.size[0] and y >= 0 and y < im.size[1]:
					pix = im.getpixel((x, y))
					psamples += 1
					color[0] += pix[0]
					color[1] += pix[1]
					color[2] += pix[2]

			if psamples > 0:
				return (int(color[0] / psamples), int(color[1] / psamples), int(color[2] / psamples),
					int(255 * alpha * psamples / samples)
				)
			else:
				return (0, 0, 0, 0)

		for y in range(im2.size[1]):
			for x in range(im2.size[0]):
				radius = float(y) / 2
				#radius += 1
				alpha = float(im2.size[1] - y) / im2.size[1]
				alpha *= alpha
				alpha *= 0.5
				im2.putpixel((x, y), blur(im, (x-extsize, y), radius, 16, alpha))

		im2.save("output/code/%sRefl.png" % match.group(1), "PNG", optimize=1)