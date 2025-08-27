"""
Implement encrypted QAP with trusted setup
"""

from enum import IntEnum
import functools
import random
from py_ecc.bn128 import (
    curve_order,
    add,
    multiply,
    pairing,
    G1,
    G2,
    FQ,
    FQ2,
)
import galois
import pytest

type Matrix = list[list[int]]
type TauG1 = tuple[FQ, ...]
type TauG2 = tuple[FQ2, ...]


FIELD = galois.GF(
    21888242871839275222246405745257275088548364400416034343698204186575808495617,
    primitive_element=5,
    verify=False,
)

random.seed(100500)


def powers_of_tau(
    constraints: int, interpolation_set: int
) -> tuple[TauG1, TauG2, TauG1]:
    tau = random.randint(1, curve_order)
    # import pdb; pdb.set_trace()
    powers_of_tau_g1 = tuple(
        multiply(G1, tau**x) for x in range(constraints - 1, -1, -1)
    )
    powers_of_tau_g2 = tuple(
        multiply(G2, tau**x) for x in range(constraints - 1, -1, -1)
    )
    t_of_tau = galois.Poly.Roots(interpolation_set, field=FIELD)(tau)
    t_of_tau_g1 = tuple(
        multiply(G1, int(t_of_tau) * tau**x) for x in range(constraints - 2, -1, -1)
    )
    return powers_of_tau_g1, powers_of_tau_g2, t_of_tau_g1


def build_interpolation_set(constraints: int) -> tuple[int, ...]:
    start = random.randint(1, curve_order // 2)
    increment = random.randint(13, 547)
    return tuple(start + increment * x for x in range(0, constraints))


def to_poly(
    matrix: Matrix,
    witness: list[int],
    interpolation_set: list[int],
) -> galois.Poly:
    result = galois.Poly.Zero(field=FIELD)
    for col in range(len(matrix[0])):
        coeffs = []
        for row in range(len(matrix)):
            coeffs.append(matrix[row][col] % FIELD.order)
        result += galois.lagrange_poly(interpolation_set, FIELD(coeffs)) * witness[col]
    return result


def at_tau_g(coefficients: galois.Array, tau_g: TauG1 | TauG2) -> FQ | FQ2:
    assert len(coefficients) == len(tau_g), "coefficients size is not equal"
    return functools.reduce(add, map(multiply, tau_g, [int(x) for x in coefficients]))


def prove(
    A: Matrix,
    B: Matrix,
    O: Matrix,
    witness: list[int],
    tau_g1: TauG1,
    tau_g2: TauG2,
    t_of_tau_g1: TauG1,
    interpolation_set: galois.Array,
    allow_fake_proof: bool = False,
) -> tuple[FQ, FQ2, FQ]:
    constraints = len(A)
    A_poly = to_poly(A, witness, interpolation_set)
    B_poly = to_poly(B, witness, interpolation_set)
    O_poly = to_poly(O, witness, interpolation_set)
    T_poly = galois.Poly.Roots(interpolation_set)
    h_poly = (A_poly * B_poly - O_poly) // T_poly
    if not allow_fake_proof:
        remainder = (A_poly * B_poly - O_poly) % T_poly
        assert remainder == galois.Poly.Zero(field=FIELD), "can't construct h_poly"

    A_at_tau_g1 = at_tau_g(A_poly.coefficients(order="desc", size=constraints), tau_g1)
    B_at_tau_g2 = at_tau_g(B_poly.coefficients(order="desc", size=constraints), tau_g2)
    O_at_tau_g1 = at_tau_g(O_poly.coefficients(order="desc", size=constraints), tau_g1)
    HT_at_tau_g1 = at_tau_g(
        h_poly.coefficients(order="desc", size=constraints - 1), t_of_tau_g1
    )
    C_at_tau_g1 = add(O_at_tau_g1, HT_at_tau_g1)
    return A_at_tau_g1, B_at_tau_g2, C_at_tau_g1


def verify(A_g1: FQ, B_g2: FQ2, C_g1: FQ) -> bool:
    return pairing(B_g2, A_g1) == pairing(G2, C_g1)


class Color(IntEnum):
    RED = 1
    BLUE = 2
    GREEN = 3
    NOT_EXISTS_PURPLE = 4
    NOT_EXISTS_ORANGE = 5


@pytest.mark.parametrize(
    "color1,color2,expected",
    [
        (Color.RED, Color.BLUE, True),
        (Color.RED, Color.GREEN, True),
        (Color.RED, Color.NOT_EXISTS_PURPLE, False),
        (Color.RED, Color.NOT_EXISTS_ORANGE, False),
        (Color.RED, Color.RED, False),
        (Color.GREEN, Color.BLUE, True),
        (Color.GREEN, Color.GREEN, False),
        (Color.GREEN, Color.NOT_EXISTS_PURPLE, False),
        (Color.GREEN, Color.NOT_EXISTS_ORANGE, False),
        (Color.GREEN, Color.RED, True),
        (Color.BLUE, Color.BLUE, False),
        (Color.BLUE, Color.GREEN, True),
        (Color.BLUE, Color.NOT_EXISTS_PURPLE, False),
        (Color.BLUE, Color.NOT_EXISTS_ORANGE, False),
        (Color.BLUE, Color.RED, True),
    ],
)
def test_qap_at_points_3_coloring(color1: Color, color2: Color, expected: bool) -> None:
    """
    3 coloring problem from howework8
    """
    x = color1.value
    y = color2.value
    a = x * y
    b = a * a
    c = x * x
    d = y * y
    witness = [1, x, y, a, b, c, d]
    A = [
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1],
    ]
    B = [
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [-36, 0, 0, 11, -1, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
    ]
    O = [
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [-36, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [6, -11, 0, 0, 0, 6, 0],
        [0, 0, 0, 0, 0, 0, 1],
        [6, 0, -11, 0, 0, 0, 6],
    ]
    constraints = len(A)
    interpolation_set = build_interpolation_set(constraints)
    tau_g1, tau_g2, t_of_tau_g1 = powers_of_tau(constraints, interpolation_set)
    Ag1, Bg2, Cg1 = prove(
        A,
        B,
        O,
        witness,
        tau_g1,
        tau_g2,
        t_of_tau_g1,
        FIELD(interpolation_set),
        allow_fake_proof=True,
    )
    assert verify(Ag1, Bg2, Cg1) == expected


@pytest.mark.parametrize(
    "x,y,noise,expected",
    [
        (100, 100, 0, True),
        (100, 100, 1, False),
    ],
)
def test_qap_at_points_3_some_function(
    x: int, y: int, noise: int, expected: bool
) -> None:
    """
    3 coloring problem from howework8
    """

    # this is our orignal formula
    out = (
        3 * x * x * y + 5 * x * y - x - 2 * y + 3
    )  # the witness vector with the intermediate variables inside
    v1 = 3 * x * x
    v2 = v1 * y
    witness = [1, out, x, y + noise, v1, v2]

    A = [[0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0]]
    B = [[0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 5, 0, 0]]
    O = [[0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [-3, 1, 1, 2, 0, -1]]
    constraints = len(A)
    interpolation_set = build_interpolation_set(constraints)
    tau_g1, tau_g2, t_of_tau_g1 = powers_of_tau(constraints, interpolation_set)
    Ag1, Bg2, Cg1 = prove(
        A,
        B,
        O,
        witness,
        tau_g1,
        tau_g2,
        t_of_tau_g1,
        FIELD(interpolation_set),
        allow_fake_proof=True,
    )
    assert verify(Ag1, Bg2, Cg1) == expected


if __name__ == "__main__":
    pytest.main([__file__])
