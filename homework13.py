"""
Implement encrypted Groth16 with public input
"""

from dataclasses import dataclass
import functools
import typing
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
    final_exponentiate,
)
import galois
import pytest

type Matrix = list[list[int]]

# Elliptic curve points can be None (point at infinity)
type G1Point = tuple[FQ, FQ] | None
type G2Point = tuple[FQ2, FQ2] | None
type TauG1 = tuple[G1Point, ...]
type TauG2 = tuple[G2Point, ...]


FIELD = galois.GF(
    curve_order,
    primitive_element=5,
    verify=False,
)

random.seed(100500)


class TrustedSetupError(Exception):
    pass


class NonZeroRemainder(Exception):
    pass


@dataclass(frozen=True, slots=True)
class TrustedSetup:
    powers_of_tau_g1: TauG1
    powers_of_tau_g2: TauG2
    t_of_tau_g1: TauG1
    alfa_g1: G1Point
    beta_g2: G2Point
    delta_g2: G2Point
    gamma_g2: G2Point
    psi: tuple[G1Point, ...]
    tau_g1: G1Point
    tau_g2: G2Point
    l: int


@dataclass(frozen=True, slots=True)
class Polinomials:
    m: int
    n: int
    a_polys: list[galois.Poly]
    b_polys: list[galois.Poly]
    c_polys: list[galois.Poly]
    t_poly: galois.Poly


def prepare_trusted_setup(
    interpolation_set: tuple[int, ...],
    polynomials: Polinomials,
    l: int
) -> TrustedSetup:
    tau = random.randint(1, curve_order)
    alfa = random.randint(1, curve_order)
    beta = random.randint(1, curve_order)
    delta = random.randint(1, curve_order)
    gamma = random.randint(1, curve_order)
    powers_of_tau_g1 = tuple(
        multiply(G1, tau**x) for x in range(polynomials.n - 1, -1, -1)
    )
    powers_of_tau_g2 = tuple(
        multiply(G2, tau**x) for x in range(polynomials.n - 1, -1, -1)
    )
    t_of_tau = galois.Poly.Roots(interpolation_set, field=FIELD)(tau)
    
    t_of_tau_g1 = tuple(
        multiply(G1, int(t_of_tau * tau**x / FIELD(delta))) for x in range(polynomials.n - 2, -1, -1)
    )
    psi = []
    assert (
        len(polynomials.a_polys) == len(polynomials.b_polys) == len(polynomials.c_polys)
    )

    for idx in range(l):
        psi_i = (
            polynomials.a_polys[idx](tau) * beta
            + polynomials.b_polys[idx](tau) * alfa
            + polynomials.c_polys[idx]
        )
        psi.append(multiply(G1, int(psi_i(tau) / FIELD(gamma))))

    for idx in range(l, polynomials.m):
        psi_i = (
            polynomials.a_polys[idx](tau) * beta
            + polynomials.b_polys[idx](tau) * alfa
            + polynomials.c_polys[idx]
        )  
        psi.append(multiply(G1, int(psi_i(tau) / FIELD(delta))))

    return TrustedSetup(
        powers_of_tau_g1=powers_of_tau_g1,
        powers_of_tau_g2=powers_of_tau_g2,
        t_of_tau_g1=t_of_tau_g1,
        alfa_g1=multiply(G1, alfa),
        beta_g2=multiply(G2, beta),
        psi=tuple(psi),
        tau_g1=multiply(G1, tau),
        tau_g2=multiply(G2, tau),
        delta_g2=multiply(G2, delta),
        gamma_g2=multiply(G2, gamma),
        l=l,
    )


def build_interpolation_set(constraints: int) -> galois.Array:
    start = random.randint(1, curve_order // 2)
    increment = random.randint(13, 547)
    return FIELD(tuple(start + increment * x for x in range(0, constraints)))


def to_polys(
    matrix: Matrix,
    interpolation_set: list[int] | galois.Array,
) -> list[galois.Poly]:
    result = []
    for col in range(len(matrix[0])):
        coeffs = []
        for row in range(len(matrix)):
            coeffs.append(matrix[row][col] % FIELD.order)
        result.append(galois.lagrange_poly(interpolation_set, FIELD(coeffs)))
    return result


def prepare_polinomials(
    A: Matrix, B: Matrix, C: Matrix, interpolation_set: galois.Array, m: int, n: int
) -> Polinomials:
    a_polys = to_polys(A, interpolation_set)
    b_polys = to_polys(B, interpolation_set)
    c_polys = to_polys(C, interpolation_set)
    t_poly = galois.Poly.Roots(interpolation_set)
    return Polinomials(
        m=m,
        n=n,
        a_polys=a_polys,
        b_polys=b_polys,
        c_polys=c_polys,
        t_poly=t_poly,
    )


def prove(
    polynomials: Polinomials,
    witness: list[int],
    ts: TrustedSetup,
    allow_fake_proof: bool = False,
) -> tuple[G1Point, G2Point, G1Point]:
    def compute(polys: list[galois.Poly], witness: list[int]) -> galois.Poly:
        assert len(polys) == len(witness)
        return sum(
            map(lambda x, y: x * y, polys, witness), galois.Poly.Zero(field=FIELD)
        )

    def calculate_h(
        a: galois.Poly, b: galois.Poly, c: galois.Poly, t: galois.Poly
    ) -> galois.Poly:
        numerator = a * b - c
        h_poly = numerator // t
        if not allow_fake_proof:
            remainder = numerator % t
            if remainder != galois.Poly.Zero(field=FIELD):
                raise NonZeroRemainder
        return h_poly

    def at_tau_g(coefficients: galois.Array, tau_g: TauG1 | TauG2) -> G1Point | G2Point:
        return functools.reduce(
            add, map(multiply, tau_g, [int(x) for x in coefficients])
        )

    a_poly = compute(polynomials.a_polys, witness)
    b_poly = compute(polynomials.b_polys, witness)
    c_poly = compute(polynomials.c_polys, witness)

    a_at_tau_g1 = typing.cast(
        G1Point,
        add(
            ts.alfa_g1,
            at_tau_g(
                a_poly.coefficients(order="desc", size=polynomials.n),
                ts.powers_of_tau_g1,
            ),
        ),
    )
    b_at_tau_g2 = typing.cast(
        G2Point,
        add(
            ts.beta_g2,
            at_tau_g(
                b_poly.coefficients(order="desc", size=polynomials.n),
                ts.powers_of_tau_g2,
            ),
        ),
    )
    h_poly = calculate_h(a_poly, b_poly, c_poly, polynomials.t_poly)
    psi = functools.reduce(add, map(lambda x, y: multiply(x, y), ts.psi[ts.l:], witness[ts.l:]))
    
    ht_at_tau_g1 = typing.cast(
        G1Point,
        at_tau_g(
            h_poly.coefficients(order="desc", size=polynomials.n - 1),
            ts.t_of_tau_g1,
        ),
    )
    c_at_tau_g1 = typing.cast(G1Point, add(psi, ht_at_tau_g1))
    return a_at_tau_g1, b_at_tau_g2, c_at_tau_g1


def verify(A_g1: G1Point, B_g2: G2Point, C_g1: G1Point, ts: TrustedSetup, public: list[int]) -> bool:
    x1 = functools.reduce(add, map(multiply, ts.psi[:ts.l], public))
    return final_exponentiate(pairing(B_g2, A_g1)) == final_exponentiate(
        pairing(ts.delta_g2, C_g1) * pairing(ts.beta_g2, ts.alfa_g1) * pairing(ts.gamma_g2, x1)
    )


@pytest.mark.parametrize(
    "x,y,noise,expected",
    [
        (10, 10, 0, True),
        (100, 100, 1, False),
    ],
)
def test_qap_at_points_3_some_function(
    x: int, y: int, noise: int, expected: bool
) -> None:
    # this is our orignal formula
    out = (
        3 * x * x * y + 5 * x * y - x - 2 * y + 3
    )  # the witness vector with the intermediate variables inside
    v1 = 3 * x * x
    v2 = v1 * y
    witness = [1, out, x, y + noise, v1, v2]
    public_input = witness[:2]

    A = [[0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0]]
    B = [[0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 5, 0, 0]]
    С = [[0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [-3, 1, 1, 2, 0, -1]]
    constraints = len(A)
    m = len(A[0])
    interpolation_set = build_interpolation_set(constraints)
    polynomials = prepare_polinomials(A, B, С, interpolation_set, m, constraints)
    ts = prepare_trusted_setup(tuple(interpolation_set), polynomials, len(public_input))
    Ag1, Bg2, Cg1 = prove(
        polynomials,
        witness,
        ts,
        allow_fake_proof=True,
    )
    assert verify(Ag1, Bg2, Cg1, ts, public_input) == expected


if __name__ == "__main__":
    pytest.main([__file__])
