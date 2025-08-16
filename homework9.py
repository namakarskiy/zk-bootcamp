import pytest
import random
from galois import GF, lagrange_poly, Poly

random.seed(100500)
FIELD_ORDER = 103

# NOTE: vec and matrix sizes os not validated for simplicity


# ======== problem 1
def vectors(vec1: list[int], vec2: list[int], field: GF) -> bool:
    """
    Alice and Bob have two vectors, and they want to test if they are the same vector.
    Assume that they evaluate their polynomials honestly. Write the code they would use to turn their vector into a polynomial over a finite field.
    """
    xs = field(list(range(len(vec1))))
    first = lagrange_poly(xs, field([x % field.order for x in vec1]))
    second = lagrange_poly(xs, field([x % field.order for x in vec2]))
    tau = random.randint(1, field.order)
    return first(tau) == second(tau)


# ======== problem 2
def matrices(
    mt1: list[list[int]], mt2: list[list[int]], vec: list[int], field: GF
) -> bool:
    """
    Alice and Bob have matrices A and B. They want to know if, for some v that

    Av = Bv

    Here, the matrices A and B have n rows and m columns.
    """
    def to_poly(mt: list[list[int]], vector: list[int]) -> Poly:
        result = Poly([0], field=field)
        xs = field(list(range(len(mt))))
        for col in range(len(mt[0])):
            coeffs = []
            for row in range(len(mt)):
                coeffs.append(mt[row][col] % field.order)
            result += lagrange_poly(xs, field(coeffs)) * (vector[col] % field.order)
        return result

    mt1_poly = to_poly(mt1, vec)
    mt2_poly = to_poly(mt2, vec)
    tau = random.randint(1, field.order)
    return mt1_poly(tau) == mt2_poly(tau)


@pytest.mark.parametrize(
    "a,b,result",
    [
        ([1, 2, 3], [1, 2, 3], True),
        ([1, 2, 3], [1, 2, 4], False),
        ([0, 0, 0], [1, 2, 4], False),
        ([-1, 107, 4], [-1, 107, 4], True),
    ],
)
def test_check_vectors(a: list[int], b: list[int], result: bool) -> None:
    field = GF(FIELD_ORDER)
    assert vectors(a, b, field) == result


@pytest.mark.parametrize(
    "a,b,vec,result",
    [
        (
            [
                [9, 4, 5],
                [8, 3, 4],
                [7, 9, 11],
            ],
            [
                [2, 4, 6],
                [1, 3, 5],
                [7, 9, 11],
            ],
            [1, 2, 7],
            True,
        ),
        (
            [
                [9, 4, 5],
                [8, 3, 4],
                [7, 9, 11],
            ],
            [
                [2, 4, 6],
                [1, 50, 5],
                [7, 9, 11],
            ],
            [1, 2, 7],
            False,
        ),
        (
            [
                [1, -2, 3],
                [4, -5, 6],
                [7, -8, 9],
            ],
            [
                [1, -2, 3],
                [4, -5, 6],
                [7, -8, 9],
            ],
            [1, 2, 7],
            True,

        )
    ],
)
def test_check_matrices(
    a: list[list[int]], b: list[list[int]], vec: list[int], result: bool
) -> None:
    field = GF(FIELD_ORDER)
    assert matrices(a, b, vec, field) == result


if __name__ == "__main__":
    pytest.main([__file__])
