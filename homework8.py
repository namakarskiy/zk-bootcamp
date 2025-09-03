from typing import Sequence
import pytest
from enum import IntEnum
import itertools
from py_ecc.bn128 import G1, G2, pairing, add, multiply, curve_order
from py_ecc.fields import (
    bn128_FQ as FQ,
    bn128_FQ2 as FQ2,
    bn128_FQ12 as FQ12,
)


class Color(IntEnum):
    RED = 1
    BLUE = 2
    GREEN = 3


def matrix_vec(mt: list[list[int]], vec: list[int]) -> list[int]:
    assert len(mt[0]) == len(vec)
    result = [0] * len(vec)
    for i in range(len(mt)):
        for j in range(len(mt[0])):
            result[i] += mt[i][j] * vec[j]
    return result


def hadamard(vec1: list[int], vec2: list[int]) -> list[int]:
    result = [0] * len(vec1)
    for i in range(len(vec1)):
        result[i] = vec1[i] * vec2[i]
    return result


type ECPointList = list[tuple[FQ, FQ]] | list[tuple[FQ2, FQ2]]


def matrix_vec_point(mt: list[list[int]], vec: ECPointList) -> ECPointList:
    assert len(mt[0]) == len(vec)
    result = [None] * len(vec)
    for i in range(len(mt)):
        for j in range(len(mt[0])):
            result[i] = add(result[i], multiply(vec[j], mt[i][j] % curve_order))
    return result


def hadamard_points(vec1: list[FQ], vec2: list[FQ2]) -> list[FQ12]:
    assert len(vec1) == len(vec2)
    result = [None] * len(vec1)
    print(f"vec2 is {'G2' if len(vec2[0]) == 4 else 'G1'}")
    for i in range(len(vec1)):
        result[i] = pairing(vec2[i], vec1[i])
    return result


def vec_to_g(vec: Sequence[int], g: FQ | FQ2) -> ECPointList:
    result = [0] * len(vec)
    for i in range(len(vec)):
        result[i] = multiply(g, vec[i] % curve_order)
    return result


# ======== problem 1


def graph_3_coloring_constraints(first: Color, second: Color) -> None:
    """
    Create a graph with 2 nodes and 1 edge and write constraints for a 3-coloring. T the 3-coloring to a rank 1 constraint system.
    If you forgot how to do this, consult the chapter on arithmetic circuits.
    """
    assert (first - Color.RED) * (first - Color.BLUE) * (first - Color.GREEN) == 0, (
        "first ne"
    )
    assert (second - Color.RED) * (second - Color.BLUE) * (second - Color.GREEN) == 0, (
        "second ne"
    )
    assert (Color.RED * Color.BLUE - first * second) * (
        Color.BLUE * Color.GREEN - first * second
    ) * (Color.GREEN * Color.RED - first * second) == 0, "same color"


# ======== problem 2


def graph_3_coloring_r1cs(w: list[int]) -> bool:
    """
    Write python code that takes an R1CS matrix A, B, and C and a witness vector w and
    verifies.

    *Aw* ⊙ *Bw* − *Cw* = 0

    Where ⊙ is the hadamard (element-wise) product.

    Use this to code to check your answer above is correct.
    """
    # constraints in function above above expands to following polinomials
    # 1) -x**3*y**3 + 11*x**2*y**2 - 36*x*y + 36 = 0
    # 2) x**3 - 6*x**2 + 11*x -6 = 0
    # 3) y**3 - 6*y**2 + 11*y -6 = 0
    # for r1cs we can have only one multiplication per constraint so we can transform it to following system of equations
    # 1) x*y = a
    # 2) a*a = b
    # 3) a*(-b + 11*a - 36) = -36
    # 4) x*x = c
    # 5) c*x = 6*c - 11*x + 6
    # 6) y*y = d
    # 7) d*y = 6*d - 11*y + 6

    # our witness in that case will be [1, x, y, a, b, c, d] and L, R, O is encoded below
    L = [
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1],
    ]
    R = [
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [-36, 0, 0, 11, -1, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
    ]
    C = [
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [-36, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [6, -11, 0, 0, 0, 6, 0],
        [0, 0, 0, 0, 0, 0, 1],
        [6, 0, -11, 0, 0, 0, 6],
    ]
    return hadamard(matrix_vec(L, w), matrix_vec(R, w)) == matrix_vec(C, w)


def graph_3_coloring_r1cs_points(wG1: list[FQ], wG2: list[FQ2]) -> bool:
    """
    Given an R1CS of the form above

    L[w in G2] * R[w in G2] = O * [G2]

    Where L, R, and O are n x m matrices of field elements and **s** is a vector of G1, G2, or G1 points

    Write python code that verifies the formula.

    You can check the equality of G12 points in Python this way:

    ```python
    a = pairing(multiply(G2, 5), multiply(G1, 8))
    b = pairing(multiply(G2, 10), multiply(G1, 4))
    eq(a, b)
    ```

    **Hint:** Each row of the matrices is a separate pairing.

    **Hint:** When you get **s** encrypted with both G1 and G2 generators, you don’t know whether or not they have the same discrete logarithm.
    However, it is straightforward to check using another equation. Figure out how to discover if sG1 == sG2 if you are given the elliptic curve points
    but not s.c
    """

    # check that points in wG1 and wG2 are the same
    assert hadamard_points(wG1, [G2] * len(wG1)) == hadamard_points(
        [G1] * len(wG2), wG2
    )
    L = [
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1],
    ]
    R = [
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [-36, 0, 0, 11, -1, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0],
    ]
    C = [
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [-36, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [6, -11, 0, 0, 0, 6, 0],
        [0, 0, 0, 0, 0, 0, 1],
        [6, 0, -11, 0, 0, 0, 6],
    ]
    return hadamard_points(
        matrix_vec_point(L, wG1), matrix_vec_point(R, wG2)
    ) == hadamard_points(matrix_vec_point(C, wG1), [G2] * len(C[0]))


@pytest.mark.parametrize("color", [Color.RED, Color.GREEN, Color.BLUE])
def test_3_coloring_constraints_not_happy_path(color: Color) -> None:
    with pytest.raises(AssertionError) as e:
        graph_3_coloring_constraints(color, color)
    assert str(e.value).startswith("same color")


@pytest.mark.parametrize(
    "a,b", [x for x in itertools.permutations([Color.RED, Color.GREEN, Color.BLUE], 2)]
)
def test_3_coloring_contraints_happy_path(a: Color, b: Color) -> None:
    graph_3_coloring_constraints(a, b)


@pytest.mark.parametrize(
    "x_color,y_color",
    [x for x in itertools.permutations([Color.RED, Color.GREEN, Color.BLUE], 2)],
)
def test_3_coloring_r1cs_happy_path(x_color: Color, y_color: Color) -> None:
    x = x_color.value
    y = y_color.value
    a = x * y
    b = a * a
    c = x * x
    d = y * y
    w = [1, x, y, a, b, c, d]
    assert graph_3_coloring_r1cs(w)


@pytest.mark.parametrize("color", [Color.RED, Color.GREEN, Color.BLUE])
def test_3_coloring_r1cs_not_happy_path(color: Color) -> None:
    x = color.value
    y = color.value
    a = x * y
    b = a * a
    c = x * x
    d = y * y
    w = [1, x, y, a, b, c, d]
    assert not graph_3_coloring_r1cs(w)


@pytest.mark.parametrize(
    "x_color,y_color",
    [x for x in itertools.permutations([Color.RED, Color.GREEN, Color.BLUE], 2)],
)
def test_3_coloring_r1cs_not_happy_path_mess_constraints(
    x_color: Color, y_color: Color
) -> None:
    x = x_color.value
    y = y_color.value
    a = x * y
    b = a * a
    c = x * x
    d = y * y
    w = [1, x, y, a + 1, b, c, d]
    assert not graph_3_coloring_r1cs(w)


@pytest.mark.parametrize("color", [Color.RED, Color.GREEN, Color.BLUE])
def test_3_coloring_r1cs_points_not_happy_path(color: Color) -> None:
    x = color.value
    y = color.value
    a = x * y
    b = a * a
    c = x * x
    d = y * y
    w = [1, x, y, a, b, c, d]
    wG1 = vec_to_g(w, G1)
    wG2 = vec_to_g(w, G2)
    assert not graph_3_coloring_r1cs_points(wG1, wG2)


def test_3_coloring_r1cs_points_mess_up_w() -> None:
    x = Color.RED.value
    y = Color.GREEN.value
    a = x * y
    b = a * a
    c = x * x
    d = y * y
    w = [1, x, y, a, b, c, d]
    w_messed = [1, x + 1, y, a, b, c, d]
    wG1 = vec_to_g(w, G1)
    wG2 = vec_to_g(w_messed, G2)
    with pytest.raises(AssertionError):
        graph_3_coloring_r1cs_points(wG1, wG2)


@pytest.mark.parametrize(
    "x_color,y_color",
    [x for x in itertools.permutations([Color.RED, Color.GREEN, Color.BLUE], 2)],
)
def test_3_coloring_r1cs_points_happy_path(x_color: Color, y_color: Color) -> None:
    x = x_color.value
    y = y_color.value
    a = x * y
    b = a * a
    c = x * x
    d = y * y
    w = [1, x, y, a, b, c, d]
    wG1 = vec_to_g(w, G1)
    wG2 = vec_to_g(w, G2)
    assert graph_3_coloring_r1cs_points(wG1, wG2)


if __name__ == "__main__":
    pytest.main([__file__])
