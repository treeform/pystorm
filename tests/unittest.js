

function fetch_url(url) {

    var req = null;

    try { req = new ActiveXObject("Msxml2.XMLHTTP"); } catch(e) {}
    if (req == null) {
	try { req = new ActiveXObject("Microsoft.XMLHTTP"); } catch(e) {}
    }
    if (req == null) {
	try { req = new XMLHttpRequest(); } catch(e) {}
    }

    req.open("get",url,false);
    req.send("");

    return req.responseText;
}

function tests_start() {
}

function tests_end() {
}

jsresults = "";

function test(path) {
	var jsurl = path + ".js";
	var pyouturl = path + "_py.out";

	var globals = {};
	var g;
	for(g in window) {
		globals[g] = true;
	}

	var jscode = fetch_url(jsurl);
	
	print = function(str) {
		jsresults += str;
		jsresults += "\n";
	}

	jsresults = "";
	eval(jscode);

	for(g in window) {
		if (!(g in globals) && (g != "location") && (g != "addEventListener")) {
			delete window[g];

		}
	}

	var pyresults = fetch_url(pyouturl)

	document.write(path + ":" + (jsresults===pyresults?"PASS":"FAIL") + "\n");
}
