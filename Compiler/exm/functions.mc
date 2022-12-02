fun pow(x, u) {
	var ret = 1;

	for (var i = 0; i < u; i = i + 1) {
		ret = ret * x;
	}

	return ret;
}

fun sqrt(x, max) {
	var ret = 1;

	for (var i = 0; i < max; i = i + 1) {
		ret = ret - (pow(ret, 2) - x) / (2 * ret);
	}

	return ret;
}

fun main() {
	print "sqrt: ";
	print sqrt(pow(72727, 2), 21);
}

main();
