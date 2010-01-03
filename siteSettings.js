var settingsPopupDisplayed = false;


function setGlobalTextColor(color) {
	var doc = document.getElementsByClassName('c3');
	for (var i = 0; i < doc.length; ++i) {
	   doc[i].style.color = color;
	}
}


function enableGlobalTextShadows() {
	var doc = document.getElementsByClassName('c3');
	for (var i = 0; i < doc.length; ++i) {
	   doc[i].style.textShadow = "2px 1px 4px rgba(0, 0, 0, 0.6)";
	}
}


function disableGlobalTextShadows() {
	var doc = document.getElementsByClassName('c3');
	for (var i = 0; i < doc.length; ++i) {
	   doc[i].style.textShadow = "none";
	}
}


function SiteSettings() {
	this.version = "4";

	/*	WebKit switches text rendering libraries/algorithms when using shadows,
		resulting in slightly thinner acute lines in the glyphs. As a result, the text
		look darker. Thus this script adjusts for that by bumping up the brightness
		from the default #f0f0f0 to full white.
	*/
	if (navigator.userAgent.indexOf("WebKit") != -1) {
		this.textColor = "rgb(255,255,255)";
	} else {
		this.textColor = "rgb(240,240,240)";
	}

	this.bgColor = "rgb(77,77,77)";

	this.useTextShadows = true;
	this.update = SiteSettings_update;
	this.serialize = SiteSettings_serialize;
	this.unserialize = SiteSettings_unserialize;
	this.useHorizontalGradient = true;
	this.useVerticalGradient = true;
}

function SiteSettings_update() {
	setGlobalTextColor(this.textColor);
	document.body.style.backgroundColor = this.bgColor;

	if (this.useTextShadows) {
		enableGlobalTextShadows();
	} else {
		disableGlobalTextShadows();
	}

	var hgradient = document.getElementById("wrapper2");
	if (!this.useHorizontalGradient) {
		hgradient.style.background = "transparent";
	} else {
		updateHorizontalGradient();
	}

	var vgradient = document.getElementById("wrapper1");
	if (!this.useVerticalGradient) {
		vgradient.style.background = "transparent";
	} else {
		vgradient.style.background = "url(vert.png) repeat-x rgb(77, 77, 77)";
	}

	set_cookie("siteSettings", this.serialize());
}

function SiteSettings_serialize() {
	var s = "";
	s += this.version;
	s += ":";
	s += this.textColor;
	s += ":";
	s += this.bgColor;
	s += ":";
	s += this.useTextShadows;
	s += ":";
	s += this.useHorizontalGradient;
	s += ":";
	s += this.useVerticalGradient;
	return s;
}

function parseBool(s) {
	return s == "true";
}

function parseRGB(s) {
	var s2 = s.substr(4, s.length-5).split(",");
	return [parseInt(s2[0]), parseInt(s2[1]), parseInt(s2[2])];
}

function formatRGB(r, g, b) {
	return "rgb("+r+","+g+","+b+")";
}

function SiteSettings_unserialize(s) {
	var parts = s.split(":")
	if (parts[0] != this.version) {
		return false;
	}
	this.textColor = parts[1];
	this.bgColor = parts[2];
	this.useTextShadows = parseBool(parts[3]);
	this.useHorizontalGradient = parseBool(parts[4]);
	this.useVerticalGradient = parseBool(parts[5]);
	siteSettings.update();
	return true;
}

var siteSettings = new SiteSettings();

function restoreDefaultSettings() {
	siteSettings = new SiteSettings();
	siteSettings.update();
	
	/* update the form's values */
	settingsPopupDisplayed = false;
	showHideSettingsPopup();
}

function showHideSettingsPopup() {
	var popup = document.getElementById("settingsPopupWrap");
	if (settingsPopupDisplayed) {
		popup.style.visibility = "hidden";
		settingsPopupDisplayed = false;
	} else {
		popup.style.visibility = "visible";
		settingsPopupDisplayed = true;

		document.getElementById("settingsUseShadowsCheckbox")
			.checked = siteSettings.useTextShadows;

		document.getElementById("settingsUseHGradientCheckbox")
			.checked = siteSettings.useHorizontalGradient;

		document.getElementById("settingsUseVGradientCheckbox")
			.checked = siteSettings.useVerticalGradient;

		var bgRGB = parseRGB(siteSettings.bgColor);
		var textRGB = parseRGB(siteSettings.textColor);

		function updateSlider(name, value) {
			document.getElementById(name)
				.value = value;
			fdSliderController.updateSlider(name);
		}

		updateSlider("bgColorSliderR", bgRGB[0]);
		updateSlider("bgColorSliderG", bgRGB[1]);
		updateSlider("bgColorSliderB", bgRGB[2]);

		updateSlider("textColorSliderR", textRGB[0]);
		updateSlider("textColorSliderG", textRGB[1]);
		updateSlider("textColorSliderB", textRGB[2]);
	}
}

function updateTextColor() {
	var r = parseInt(document.getElementById('textColorSliderR').value, 10) || 0;
	var g = parseInt(document.getElementById('textColorSliderG').value, 10) || 0;
	var b = parseInt(document.getElementById('textColorSliderB').value, 10) || 0;
	siteSettings.textColor = formatRGB(r, g, b);
	siteSettings.update();
}

function updateBGColor() {
	var r = parseInt(document.getElementById('bgColorSliderR').value, 10) || 0;
	var g = parseInt(document.getElementById('bgColorSliderG').value, 10) || 0;
	var b = parseInt(document.getElementById('bgColorSliderB').value, 10) || 0;
	siteSettings.bgColor = formatRGB(r, g, b);
	siteSettings.update();
}

function settingsUseShadowsHandler(e) {
	siteSettings.useTextShadows = e.target.checked;
	siteSettings.update();
}

function loadStoredSettings() {
	var s = get_cookie("siteSettings");
	var success = false;
	if (s) {
		success = siteSettings.unserialize(s);
	}
	if (!success) {
		siteSettings.update();
	}
}

