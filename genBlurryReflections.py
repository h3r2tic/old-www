# Yeah, I know that Gaussian-blurring the image only varying the kernel's radius
# with distance will not give anything resembling a physically-correct reflection,
# but it looks good enough for now.

import os
import re
from PIL import Image, ImageOps
import scipy
from math import *

extsize = 28
cornerRadius = 3


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
		xf = xy[0]+xoff
		yf = xy[1]+yoff
		x = int(round(xf))
		y = int(round(yf))

		if yf < cornerRadius:
			cornerDist = 0
			if xf < cornerRadius:
				cornerDist =\
					(cornerRadius-xf)**2 +\
					(cornerRadius-yf)**2
			elif xf >= im.size[0]-cornerRadius:
				cornerDist =\
					(im.size[0]-1-cornerRadius-xf)**2 +\
					(cornerRadius-yf)**2
			if cornerDist > cornerRadius**2:
				continue

		if x >= 0 and x < im.size[0] and y >= 0 and y < im.size[1]:
			pix = im.getpixel((x, y))
			psamples += 1
			color[0] += toLinear(1.0/255 * pix[0])
			color[1] += toLinear(1.0/255 * pix[1])
			color[2] += toLinear(1.0/255 * pix[2])

	if psamples > 0:
		return (
			int(round(255 * fromLinear(color[0] / psamples))),
			int(round(255 * fromLinear(color[1] / psamples))),
			int(round(255 * fromLinear(color[2] / psamples))),
			int(round(255 * alpha * psamples / samples))
		)
	else:
		return (0, 0, 0, 0)


for fname in os.listdir('input/code/'):
	match = re.match(r"(\w+)Thumb\.jpg", fname)
	if match:
		im = Image.open("input/code/"+fname)
		im = ImageOps.flip(im)

		w, h = im.size

		im2 = Image.new("RGBA", (im.size[0] + extsize*2, 80))

		for y in range(im2.size[1]):
			for x in range(im2.size[0]):
				radius = float(y) / 2
				radius += 0.2
				alpha = float(im2.size[1] - y) / im2.size[1]
				alpha *= alpha
				#alpha *= 0.75
				im2.putpixel((x, y), blur(im, (x-extsize, y), radius, 64, alpha))

		im2.save("output/code/%sRefl.png" % match.group(1), "PNG", optimize=1)
