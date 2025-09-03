import numpy as np
import numpy.typing as npt
import random
import math
import galois

import pytest

random.seed(100500)


def qap_over_real_numbers(tau: int) -> bool:
    """
    Convert the following R1CS into a QAP over real numbers, not a finite field
    import numpy as np
    import random

    # Define the matrices
    A = np.array([[0,0,3,0,0,0],
                [0,0,0,0,1,0],
                [0,0,1,0,0,0]])

    B = np.array([[0,0,1,0,0,0],
                [0,0,0,1,0,0],
                [0,0,0,5,0,0]])

    C = np.array([[0,0,0,0,1,0],
               [0,0,0,0,0,1],
               [-3,1,1,2,0,-1]])



    # pick values for x and y
    x = 100
    y = 100

    # this is our orignal formula
    out = 3 * x * x * y + 5 * x * y - x- 2*y + 3# the witness vector with the intermediate variables inside
    v1 = 3*x*x
    v2 = v1 * y
    w = np.array([1, out, x, y, v1, v2])

    result = C.dot(w) == np.multiply(A.dot(w),B.dot(w))
    assert result.all(), "result contains an inequality"

    You can use a computer (Python, sage, etc) to check your work at each step and do the Lagrange interpolate, but you must show each step.

    **Be sure to check the polynomials manually because you will get precision loss when interpolating over floats/real numbers.**

    Check your work by seeing that the polynomial on both sides of the equation is the same.

    """
    # pick values for x and y
    x = 100
    y = 100

    # this is our orignal formula
    out = (
        3 * x * x * y + 5 * x * y - x - 2 * y + 3
    )  # the witness vector with the intermediate variables inside
    v1 = 3 * x * x
    v2 = v1 * y
    w = np.array([1, out, x, y, v1, v2])

    A = np.array([[0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0]])
    B = np.array([[0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 5, 0, 0]])
    C = np.array([[0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [-3, 1, 1, 2, 0, -1]])

    # interpolation set
    xs = np.array(list(range(len(A))))  # can use any of A, B, C

    def to_poly(
        mat: npt.NDArray[np.float64],
intepolation_set: npt.NDArray[np.int64],
        witness: npt.NDArray[np.int64],
    ) -> np.poly1d:
        result = np.poly1d([])
        for idx, ys in enumerate(mat.T):
            coefficients = np.polyfit(
                intepolation_set, ys, deg=len(intepolation_set) - 1
            )
            result += np.poly1d(coefficients) * witness[idx]
        return result

    a_poly = to_poly(A, xs, w)
    b_poly = to_poly(B, xs, w)
    c_poly = to_poly(C, xs, w)
    t_poly = np.poly1d(np.roots(xs))
    h_poly, reminder = (a_poly * b_poly - c_poly) / t_poly
    assert reminder == np.poly1d([0.0])

    left = a_poly(tau) * b_poly(tau)
    right = c_poly(tau) + h_poly(tau) * t_poly(tau)
    return math.isclose(left, right, rel_tol=1e-6)


def test_real_numbers_random_taus() -> None:
    for _ in range(100):
        tau = random.randint(-10000, 10000)
        assert qap_over_real_numbers(tau)


# problem 2


def qap_over_finite_field(tau: int, field: type[galois.FieldArray]) -> bool:
    """
    same as problem 1 but over finite field
    """
    # pick values for x and y
    x = 100
    y = 100

    # this is our orignal formula
    out = (
        3 * x * x * y + 5 * x * y - x - 2 * y + 3
    )  # the witness vector with the intermediate variables inside
    v1 = 3 * x * x
    v2 = v1 * y
    w = field([1, out, x, y, v1, v2])

    A = [[0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0]]
    B = [[0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 5, 0, 0]]
    C = [[0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [-3, 1, 1, 2, 0, -1]]

    # interpolation set
    xs = field(list(range(len(A))))  # can use any of A, B, C

    def to_poly(
        mt: list[list[int]],
        vector: galois.FieldArray,
        interpolation_set: galois.FieldArray,
    ) -> galois.Poly:
        result = galois.Poly([0], field=field)
        for col in range(len(mt[0])):
            coeffs = []
            for row in range(len(mt)):
                coeffs.append(mt[row][col] % field.order)
            result += (
                galois.lagrange_poly(interpolation_set, field(coeffs)) * vector[col]
            )
        return result

    a_poly = to_poly(A, w, xs)
    b_poly = to_poly(B, w, xs)
    c_poly = to_poly(C, w, xs)
    t_poly = galois.Poly.Roots(xs, field=field)
    h_poly = (a_poly * b_poly - c_poly) // t_poly
    remainder = (a_poly * b_poly - c_poly) % t_poly
    assert remainder == galois.Poly([0], field=field)
    return a_poly(tau) * b_poly(tau) == c_poly(tau) + h_poly(tau) * t_poly(tau)


def test_finite_field_numbers_random_taus() -> None:
    field = galois.GF(
        21888242871839275222246405745257275088548364400416034343698204186575808495617,
        primitive_element=5,
        verify=False,
    )
    for _ in range(100):
        tau = random.randint(-10000, 10000)
        assert qap_over_finite_field(tau % field.order, field=field)


if __name__ == "__main__":
    pytest.main([__file__])
