// Dibuja set de Mandelbrot!

var xmin = -2.0;
var xmax = 1.0;
var ymin = -1.5;
var ymax = 1.5;
var width = 80.0;
var height = 40.0;
var threshold = 1000;

fun in_mandelbrot(x0, y0, n) {
	var x = 0.0;
	var y = 0.0;
	var xtemp;
	while (n > 0) {
		xtemp = x*x - y*y + x0;
		y = 2.0*x*y + y0;
		x = xtemp;
		n = n - 1;
		if (x*x + y*y > 4.0) {
			return false;
		}
	}
	return true;
}

fun mandel() {
	var dx = (xmax - xmin)/width;
	var dy = (ymax - ymin)/height;

	var y = ymax;
	var x;

	while (y >= ymin) {
		x = xmin;
		var line = "";
		while (x < xmax) {
			if (in_mandelbrot(x, y, threshold)) {
				line = line + "*";
			} else {
				line = line + ".";
			}
			x = x + dx;
		}
		print line;
		y = y - dy;
	}
}

mandel();
