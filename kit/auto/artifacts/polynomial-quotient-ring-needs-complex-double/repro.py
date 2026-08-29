"""
Repro: PolynomialRing(RR).quotient(x^2 + 1) fails when sage.rings.complex_double
is not installed (e.g. in passagemath-pari).

This reproduces the failure observed in CI on sagemath_pari-check:
sage.rings.polynomial.polynomial_quotient_ring.PolynomialQuotientRing_field.absolute_degree
"""

import sys

# Simulate environment without passagemath-modules (e.g., passagemath-pari)
sys.modules["sage.rings.complex_double"] = None

from sage.rings.real_double import RDF as RR
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

R = PolynomialRing(RR, "x")
x = R.gen()

# This checks x^2 + 1.is_irreducible(), which calls .factor(),
# which calls RealDoubleField_class._factor_univariate_polynomial,
# which requires sage.rings.complex_double.CDF.
S = R.quotient(x**2 + 1)
print(S.absolute_degree())
