(function() {
	var browser = navigator.appName;
	if (browser == "Microsoft Internet Explorer") {
		var widget = document.getElementById("topStatus");
		var text = document.createTextNode("This site doesn't support Internet Explorer. Try using a standards-complaint browser, like Firefox or Chrome.");
		widget.appendChild(text)
		widget.style.display = "block";
	}
})();

