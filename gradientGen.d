module gradientGen;

import xf.omg.core.LinearAlgebra;
import xf.omg.misc.Interpolation;
import xf.omg.core.Misc;
import xf.image.Image;
import xf.image.DevilSaver;
import xf.utils.Memory;
import xf.rt.NewColor;
import tango.io.Stdout;
import tango.io.device.File;
import tango.math.random.Kiss;
import tango.text.convert.Format;


ubyte ftoub(double f) {
	if (f <= 0.0) return 0;
	if (f >= 1.0) return 255;
	return rndint(f * 255);
}


vec4ub sRGB(vec4 c, double postGammaMult = 1.0) {
	vec3d rgb = vec3d.from(c);
	vec3d srgb = gammaCorrectSRGB(rgb);
	srgb *= postGammaMult;
	return vec4ub(
		ftoub(srgb.r),
		ftoub(srgb.g),
		ftoub(srgb.b),
		ftoub(c.a)
	);
}


struct SplinePoint {
	vec4	pt;
	double	t;
}


int binomial(int n, int k) {
	if (k > n) {
        return 0;
	}
	if (k > n / 2) {
		k = n - k;
	}

	int num = 1;
	for (int i = n - k + 1; i <= n; ++i) {
		num *= i;
	}
	int den = 1;
	for (int i = 2; i <= k; ++i) {
		den *= i;
	}
	return num / den;
}

static assert (binomial(7, 3) == 35);
static assert (binomial(4, 0) == 1);
static assert (binomial(4, 1) == 4);
static assert (binomial(4, 2) == 6);
static assert (binomial(4, 3) == 4);
static assert (binomial(4, 4) == 1);


/+T bezier(T)(T delegate(int) p, int n, double t) {
	T pt = T.zero;

	double ti = 1.f;
	for (int i = 0; i < n; ++i) {
		double mult = cast(double)binomial(i, n) * ti * pow(1.f - t, n-i);
		pt += mult * p(i);
		ti *= t;
	}

	double t2 = t * t;
	double t3 = t2 * t;
		
	T pt = T.zero;
	pt += p3 * (t3 / 6.f);
	pt += p2 * ((1.f + 3.f * t + 3.f * t2 - 3.f * t3) / 6.f);
	pt += p1 * ((4.f - 6.f * t2 + 3.f * t3) / 6.f);
	pt += p0 * (((1.f - t) * (1.f - t) * (1.f - t)) / 6.f);
		
	return pt;
}+/


enum InterpType {
	CatmullRom,
	Bezier,
	Cosine
}

enum NoiseWeighting {
	Brightness	= 0b1,
	Center		= 0b10
}


vec4 interp(InterpType type, SplinePoint[] points, double t) {
	int i1 = 0;
	while (i1+1 < points.length && points[i1+1].t < t) ++i1;
	int i0 = max(0, min(points.length-1, i1-1));
	int i2 = max(0, min(points.length-1, i1+1));
	int i3 = max(0, min(points.length-1, i1+2));
	double t2 = 1.0;
	if (i1 != i2) {
		t2 = (t - points[i1].t) / (points[i2].t - points[i1].t);
	}
	vec4 res = vec4.zero;
	if (InterpType.CatmullRom == type) {
		catmullRomInterp(
			t2,
			points[i0].pt,
			points[i1].pt,
			points[i2].pt,
			points[i3].pt,
			res
		);
	} else if (InterpType.Cosine == type) {
		double x = (1.0 - cos(t2 * pi)) * 0.5;
		res = points[i1].pt * (1.0 - x) + points[i2].pt * x;
	} else if (InterpType.Bezier == type) {
		/+res = bezier(
			points[i0].pt,
			points[i1].pt,
			points[i2].pt,
			points[i3].pt,
			t2
		);+/
		assert (false);
	} else assert (false);
	return res;
}


vec4ub generateGradient(char[] file, double alpha, int width, int height, bool vertical, double noiseStr, NoiseWeighting nwt, InterpType interpType, double[] intens, double postGammaMult = 1.0) {
	SplinePoint[] splinePoints;
	for (int i = 0; i < intens.length; i += 2) {
		splinePoints ~= SplinePoint(
			vec4(intens[i], intens[i], intens[i], alpha),
			intens[i+1]
		);
	}

	vec4ub[][] pixels = new vec4ub[][](width, height);

	vec4 genNoise() {
		static double n1() {
			return Kiss.instance.fraction() - 0.5f;
		}

		return vec4(
			n1 * noiseStr,
			n1 * noiseStr,
			n1 * noiseStr,
			0
		);
	}

	vec4 lastBase = vec4.zero;

	vec4ub finalCol(double t, vec4 colf) {
		auto noise = genNoise();
		double noiseWeight = 1.0;

		if (NoiseWeighting.Center & nwt) {
			noiseWeight *= sin(pi * t);
		}
		if (NoiseWeighting.Brightness & nwt) {
			double lumin = 0.3 * colf.r + 0.59 * colf.g + 0.11 * colf.b;
			noiseWeight *= sqrt(lumin);
		}

		colf += noise * noiseWeight;
		return sRGB(colf, postGammaMult);
	}

	if (vertical) {
		for (int x = 0; x < width; ++x) {
			double xf = x / cast(double)(width-1);
			vec4 baseCol = interp(interpType, splinePoints, xf);
			lastBase = baseCol;
			assert (baseCol.ok);

			for (int y = 0; y < height; ++y) {
				pixels[x][y] = finalCol(xf, baseCol);
			}
		}
	} else {
		for (int y = 0; y < height; ++y) {
			double yf = y / cast(double)(height-1);
			vec4 baseCol = interp(interpType, splinePoints, yf);
			lastBase = baseCol;
			assert (baseCol.ok);

			for (int x = 0; x < width; ++x) {
				pixels[x][y] = finalCol(yf, baseCol);
			}
		}
	}

	auto img = new Image;
	auto plane = new ImagePlane;
	plane.width = width;
	plane.height = height;
	plane.depth = 1;
	plane.opaque = false;
	plane.data.alloc(width*height*4);
	
	for (int x = 0; x < width; ++x) {
		for (int y = 0; y < height; ++y) {
			int off = (width*(height-y-1)+x) * 4;
			plane.data[off..off+4] = cast(ubyte[])pixels[x][y..y+1];
		}
	}

	img.imageFormat = ImageFormat.RGBA;
	img.planes ~= plane;

	scope saver = new DevilSaver;
	saver.overwrite = true;
	saver.save(img, file);

	return sRGB(lastBase, postGammaMult);
}


void main() {
	const double noise = 0.055f;

	int[] xResolutions = [
		320,
		640,
		800,
		1024,
		1152,
		1280,
		1366,
		1440,
		1600,
		1680,
		1920,
		2048,
		2560,
		2800,
		3200,
		3840,
		4096
	];

	char[] resolutionsJS = `var supportedGradientResolutions = [`\n\t;
	foreach (i, r; xResolutions) {
		if (i != 0) resolutionsJS ~= ",\n\t";
		resolutionsJS ~= Format("{}", r);
	}
	resolutionsJS ~= "\n];";
	File.set("output/supportedGradientResolutions.js", resolutionsJS);

	const double mult = 0.5f;

	foreach (xres; xResolutions) {
		auto lastH = generateGradient(
			Format("output/horiz{}.png", xres), 0.49999f,
			xres, 40, true,
			noise * 1.2f, NoiseWeighting.Brightness, InterpType.CatmullRom,
			[
				0.0 * mult, 0.0,
				0.08 * mult, 0.2,
				0.12 * mult, 0.33,
				0.12 * mult, 0.66,
				0.08 * mult, 0.8,
				0.0 * mult, 1.0
			]
		);

		Stdout.formatln("last h pt: {}", lastH);
	}


	auto lastV = generateGradient(
		"output/vert.png", 1.0,
		60, 400, false,
		noise * 1.0, NoiseWeighting.Center | NoiseWeighting.Brightness, InterpType.Cosine,
		[
			0.0 * mult, 0.0,
			0.12 * mult, 1.0
		]
	);

	Stdout.formatln("last v pt: {}", lastV);


	generateGradient(
		"output/vertB.png", 1.0,
		60, 200, false,
		noise * 1.0, NoiseWeighting.Center | NoiseWeighting.Brightness, InterpType.Cosine,
		[
			0.12 * mult, 0.0,
			0.05 * mult, 1.0
		]
	);
}

