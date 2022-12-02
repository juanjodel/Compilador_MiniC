// Fibonacci iterativo

fun fib() {
	var prev = 0; var cur = 0;
	
	fun next() {
		if (cur == 0) {
			cur = 1;
			return 0;
		}
		var res = cur;
		cur = cur + prev;
		prev = res;
		
		return res;
	}
	
	return next;
}

var next = fib();
for (var i = 0; i <= 20; i = i + 1) {
	print next();
}

