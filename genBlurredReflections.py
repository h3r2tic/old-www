import os
import re
from PIL import Image, ImageOps
import scipy
from math import *

extsize = 24


def toLinear(x):
	if x < 0.0031308 * 12.92:
		return x * (1.0 / 12.92)
	else:
		a = 0.055;
		return pow((x + a) / (1.0 + a), 2.4)

def fromLinear(x):
	if x < 0.0:
		return 0.0
	
	if x < 0.0031308:
		return x * 12.92
	else:
		a = 0.055
		return (1 + a) * pow(x, 1.0 / 2.4) - a

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
			color[0] += toLinear(pix[0])
			color[1] += toLinear(pix[1])
			color[2] += toLinear(pix[2])

	if psamples > 0:
		return (
			int(fromLinear(color[0] / psamples)),
			int(fromLinear(color[1] / psamples)),
			int(fromLinear(color[2] / psamples)),
			int(255 * alpha * psamples / samples)
		)
	else:
		return (0, 0, 0, 0)


for fname in os.listdir('input/code/'):
	match = re.match(r"(\w+)Thumb\.jpg", fname)
	if match:
		im = Image.open("input/code/"+fname)
		im = ImageOps.flip(im)

		w, h = im.size

		im2 = Image.new("RGBA", (im.size[0] + extsize*2, int(im.size[1] * 0.7)))

		for y in range(im2.size[1]):
			for x in range(im2.size[0]):
				radius = float(y) / 2
				#radius += 1
				alpha = float(im2.size[1] - y) / im2.size[1]
				alpha *= alpha
				alpha *= 0.5
				im2.putpixel((x, y), blur(im, (x-extsize, y), radius, 50, alpha))

		im2.save("output/code/%sRefl.png" % match.group(1), "PNG", optimize=1)