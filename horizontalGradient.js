function setHorizontalGradient(width) {
	if (!siteSettings.useHorizontalGradient) {
		return;
	}

	var res = supportedGradientResolutions[
		supportedGradientResolutions.length-1
	];

	for (i in supportedGradientResolutions) {
		r = supportedGradientResolutions[i];
		if (r >= width) {
			res = r;
			break;
		}
	}

	var foo = document.getElementById("wrapper2");
	foo.style.background = "url(horiz"+res+".png) repeat-y";
}


function updateHorizontalGradient() {
	setHorizontalGradient(window.innerWidth);
}


function loadHorizontalGradient() {
	updateHorizontalGradient();

	window.onresize = function() {
		updateHorizontalGradient();
	};
}

