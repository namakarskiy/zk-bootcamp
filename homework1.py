import numpy as np
import galois
from fractions import Fraction

# For all problems below, assume the finite field is p = 71.

# **Remember, this is done in a finite field so your answer should only contain numbers [0-70] inclusive. 
# There should be no fractions or negative numbers.**


# >>> -5 % p # number congruent to -5
# >>> pow(5, -1, p) # multiplicative inverse of 5



## Problem 1

# Find the elements in a finite field that are congruent to the following values:
# a) -1
# b) -4
# c) -160
# d) 500

p = 71

print("*" * 20 + " Task 1" + "*" * 20)
print(f"a={-1 % p}")
print(f"b={-4 % p}")
print(f"c={-160 % p}")
print(f"d={500 % p}")



## Problem 2
# Find the elements that are congruent to 
# a = 5/6, 
# b = 11/12
# c = 21/12


# NOTES: to find multiplicative inverse use Fermat Little Teorem or Extended Euclidian Algorithm
print("*" * 20 + " Task 2" + "*" * 20)
a = 5 * pow(6, -1, p) % p
print(f"{a=}")
b = 11 * pow(12, -1, p) % p
print(f"{b=}")
c = 21 * pow(12, -1, p) % p
print(f"{c=}")
print(f"a + b = c is {(a + b) % p == c}")


## Problem 3
# Find the elements that are congruent to a = 2/3, b = 1/2, and c = 1/3.
# Verify your answer by checking that a * b = c (in the finite field)

print("*" * 20 + " Task 3" + "*" * 20)
a = 2 * pow(3, -1, p) % p
print(f"{a=}")
b = 1 * pow(2, -1, p) % p
print(f"{b=}")
c = pow(3, -1, p) % p
print(f"{c=}")
print(f"a * b = c is {(a * b) % p == c}")

## Problem 4
# Compute the inverse of the following matrix in the finite field:  [[1,1], [1,4]]
print("*" * 20 + " Task 4" + "*" * 20)
m = [[1,1], [1,4]]
det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
assert det != 0, "Matrix doesn't have inverse"

inverse = (pow(det, -1, p) * np.array([
    [m[1][1] % p, -m[0][1] % p],
    [-m[1][0] % p, m[0][0] % p]
])) % p

print(f"Inverse is correct: {(np.matmul(np.array(m), inverse) % p == np.identity(2)).all()}")


## Problem 5
# What is the modular square root of 12?
# Verify your answer by checking that x * x = 12 (mod 71)
print("*" * 20 + " Task 5" + "*" * 20)
for x in range(71):
    if x * x  % p == 12:
        break
print(f"Roots are: {x}, {71 - x}")
        

## Problem 6
# Suppose we have the following polynomials:

# $$
# p(x)=52x^2+24x+61
# q(x)=40x^2+40x+58
# $$

# What is p(x) + q(x)? What is p(x) * q(x)?

# Use the `galois` library in Python to find the roots of p(x) and q(x).

# What are the roots of p(x)q(x)?

print("*" * 20 + " Task 6" + "*" * 20)
GF = galois.GF(p)

px = galois.Poly([52, 24, 61], field=GF)
qx = galois.Poly([40, 40, 58], field=GF)

print(f"p(x) + q(x) = {px + qx}")
print(f"p(x) * q(x) = {px * qx}")
print(f"roots p(x) = {px.roots()}")
print(f"roots q(x) = {qx.roots()}")
print(f"roots of p(x) * q(x) = {(px * qx).roots()}")


## Problem 7
# Find a polynomial f(x) that crosses the points (10, 15), (23, 29).

# Since these are two points, the polynomial will be of degree 1 and be the equation for a line (y = ax + b).

# Verify your answer by checking that f(10) = 15 and f(23) = 29.
print("*" * 20 + " Task 6" + "*" * 20)
p1 = (10, 15)
p2 = (23, 29)

slope = Fraction(p2[1] - p1[1], p2[0] - p1[0])
b = p1[1] - slope * p1[0] 


print(f"f(10) == 15 is {10 * slope + b == 15}")
print(f"f(23) == 29 is {23 * slope + b == 29}")


## Problem 8
# What is Lagrange interpolation and what does it do?

# Find a polynomial that crosses through the points (0, 1), (1, 2), (2, 1).

# Use this Stackoverflow answer as a starting point: https://stackoverflow.com/a/73434775

GF = galois.GF(p)
x = GF([0, 1, 2])
y = GF([1, 2, 1])

L = galois.lagrange_poly(x, y)
print("Lagrange polynomial:", L)
print(f"L(x) at points is equal to [1,2,1] is {all(L(x) == [1,2,1])}")