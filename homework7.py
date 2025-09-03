from dataclasses import dataclass
import pytest


def at_least_one_is_zero_circuit(signals: list[int]) -> None:
    """
    Create an arithmetic circuit that takes signals x₁, x₂, …, xₙ and is satisfied if at least one signal is 0.
    """
    total = 1
    for x in signals:
        assert x * (x - 1) == 0, "not 0 or 1"
        total *= x
    assert total == 0, "all 1s"


def test_at_least_one_is_zero_circuit():
    with pytest.raises(AssertionError) as e:
        at_least_one_is_zero_circuit([1, 2])
    assert str(e.value).startswith("not 0 or 1")

    with pytest.raises(AssertionError) as e:
        at_least_one_is_zero_circuit([1, 1, 1])
    assert str(e.value).startswith("all 1s")

    at_least_one_is_zero_circuit([1, 1, 0])


# ===========


def all_is_one_circuit(signals: list[int]) -> None:
    """
    Create an arithmetic circuit that takes signals x₁, x₂, …, xₙ and is satsified if all signals are 1.
    """
    total = 1
    for x in signals:
        assert x * (x - 1) == 0, "not 0 or 1"
        total *= x
    assert total == 1, "all 1s"


def test_all_is_one_circuit():
    with pytest.raises(AssertionError) as e:
        all_is_one_circuit([1, 2])
    assert str(e.value).startswith("not 0 or 1")

    with pytest.raises(AssertionError) as e:
        all_is_one_circuit([1, 1, 0])
    assert str(e.value).startswith("all 1s")

    all_is_one_circuit([1, 1, 1])


# ===========


@dataclass(frozen=True, slots=True)
class Node:
    color: int
    value: str


def graph_is_bipartite(graph: dict[Node, list[Node]]) -> None:
    """
    A bipartite graph is a graph that can be colored with two colors such that no two neighboring nodes share the same color.
    Devise an arithmetic circuit scheme to show you have a valid witness of a 2-coloring of a graph.
    Hint: the scheme in this tutorial needs to be adjusted before it will work with a 2-coloring.
    """

    def nodes_two_colored(x1: int, x2: int) -> None:
        assert (x1 - 1) * (x1 - 2) == 0, "x1 not 1 or 2"
        assert (x2 - 1) * (x2 - 2) == 0, "x2 not 1 or 2"
        assert x1 * x2 == 2, "not two colored"

    for node, neighbours in graph.items():
        for neighbour in neighbours:
            nodes_two_colored(node.color, neighbour.color)


def test_graph_is_bipartite():
    with pytest.raises(AssertionError) as e:
        graph_is_bipartite({Node(3, "a"): [Node(1, "b")]})
    assert str(e.value).startswith("x1 not 1 or 2")

    with pytest.raises(AssertionError) as e:
        graph_is_bipartite({Node(1, "a"): [Node(3, "b")]})
    assert str(e.value).startswith("x2 not 1 or 2")

    with pytest.raises(AssertionError) as e:
        graph_is_bipartite(
            {
                Node(2, "a"): [Node(2, "b")],
            }
        )
    assert str(e.value).startswith("not two colored")

    graph_is_bipartite({Node(1, "a"): [Node(2, "b")], Node(2, "c"): [Node(1, "c")]})


# ==========


def max_of_3_values(k: int, x: int, y: int, z: int) -> None:
    """
    Create an arithmetic circuit that constrains k to be the maximum of x, y, or z.
    That is, k should be equal to x if x is the maximum value, and same for y and z.
    """

    def gte(a: int, b: int) -> int:
        n = 4
        # NOTE: slight simplification here, would need to check constraints per bit in a form of xn*(xn - 1) == 0
        # and implement binary converson, but it doesn't really makes sense here

        assert len(bin(a)) <= n + 2, (
            "a not in range"
        )  # +2 here because bin return string in 0bxxx format
        assert len(bin(b)) <= n + 2, "b not in range"
        tmp = 2**n + (a - b)  # omiting n-1 as we want our numbers be 5 bits
        assert tmp & (1 << 4) != 0, "lte"
        return 1

    def and_gate(a: int, b: int) -> int:
        assert a * (a - 1) == 0, "not 0or1"
        assert b * (b - 1) == 0, "not 0or1"
        assert a * b == 1, "and"
        return 1

    assert (k - x) * (k - y) * (k - z) == 0, "ne"

    assert and_gate(and_gate(gte(k, x), gte(k, y)), gte(k, z))


def test_max_of_3_values() -> None:
    with pytest.raises(AssertionError) as e:
        max_of_3_values(4, 3, 2, 1)
    assert str(e.value).startswith("ne")

    with pytest.raises(AssertionError) as e:
        max_of_3_values(102, 102, 101, 100)
    assert str(e.value).startswith("a not in range")

    with pytest.raises(AssertionError) as e:
        max_of_3_values(3, 4, 3, 2)
    assert str(e.value).startswith("lte")

    max_of_3_values(4, 4, 3, 2)


# ==========


def at_least_one_is_zero(x1: int, x2: int, x3: int, x4: int) -> None:
    """
    Create an arithmetic circuit that takes signals x₁, x₂, …, xₙ, constrains them to be binary, and outputs 1 if at least one of the signals is 1.
    Hint: this is tricker than it looks. Consider combining what you learned in the first two problems and using the NOT gate.
    """
    assert x1 * (x1 - 1) == 0
    assert x2 * (x2 - 1) == 0
    assert x3 * (x3 - 1) == 0
    assert x4 * (x4 - 1) == 0
    assert (1 - x1) * (1 - x2) * (1 - x3) * (1 - x4) == 0, "all0"


def test_at_least_one_is_zero() -> None:
    with pytest.raises(AssertionError) as e:
        at_least_one_is_zero(0, 0, 0, 0)
    str(e.value).startswith("all0")
    at_least_one_is_zero(0, 1, 0, 0)
    at_least_one_is_zero(1, 1, 1, 1)
    at_least_one_is_zero(1, 1, 1, 0)


# ==========


def is_power_of_two(a: int) -> None:
    """
    Create an arithmetic circuit to determine if a signal v is a power of two (1, 2, 4, 8, etc). Hint: create an arithmetic circuit that constrains
    another set of signals to encode the binary representation of v, then place additional restrictions on those signals.
    """
    tmp = [int(x) for x in bin(a)[2:]]
    assert tmp[0] == 1, "msb not 1"
    for x in tmp[1:]:
        assert x == 0, "non zero"


def test_power_of_2():
    with pytest.raises(AssertionError) as e:
        is_power_of_two(11)
    assert str(e.value).startswith("non zero")

    with pytest.raises(AssertionError) as e:
        is_power_of_two(0)
    assert str(e.value).startswith("msb not 1")
    is_power_of_two(1)
    is_power_of_two(2)
    is_power_of_two(16)


# ==========


def is_subset_sum(k: int, subset: list[int], switches: list[int]) -> None:
    """
    Create an arithmetic circuit that models the Subset sum problem. Given a set of integers (assume they are all non-negative), determine if there is a subset that sums to a given value
    """
    subset_sum = sum([x[0] * x[1] for x in zip(subset, switches, strict=True)])
    assert subset_sum == k, "not"


def test_subset_sum():
    with pytest.raises(AssertionError) as e:
        is_subset_sum(22, [3, 5, 17, 21], [0, 1, 0, 0])
    assert str(e.value).startswith("not")
    is_subset_sum(22, [3, 5, 17, 21], [0, 1, 1, 0])


if __name__ == "__main__":
    pytest.main([__file__])
