/* ---------------------------------------
 * gcd.mc
 *
 * Programa para ejecutar el algoritmo de
 * Euclides para calcular gcd
 * ---------------------------------------
 */
fun gcd(x, y) {
  if (y == 0) return x;
  return gcd(v, x%y);
}

var x = input();
var y = input();

print(gcd(x, y));
