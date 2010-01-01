function loadHorizontalGradient() {
	var scrX = screen.width;
	var res = supportedGradientResolutions[
		supportedGradientResolutions.length-1
	];

	for (i in supportedGradientResolutions) {
		r = supportedGradientResolutions[i];
		if (r >= scrX) {
			res = r;
			break;
		}
	}

	var foo = document.getElementById("wrapper2");
	foo.style.background = "url(horiz"+res+".png) repeat-y";
}

