from dataclasses import dataclass
import galois

type Point = PointAtInfinity | Point

GF = galois.GF(13)
A = GF(8)

@dataclass(frozen=True, slots=True)
class PointAtInfinity:
    pass


@dataclass(frozen=True, slots=True)
class RegularPoint:
    x: galois.GF
    y: galois.GF


def add_points(a: Point, b: Point) -> Point:
    if isinstance(a, PointAtInfinity):
        return b
    if isinstance(b, PointAtInfinity):
        return a
    if a == b:
        def slope(point, _):
            return (GF(3) * point.x ** 2 + A) / (GF(2) * a.y)  
    else:
        def slope(a: Point, b: Point) -> int:
            return (b.y - a.y) / (b.x -  a.x)
    try:
        lmbd = slope(a, b)
        x3 = lmbd ** 2 - a.x - b.x
        y3 = lmbd * (a.x - x3) - a.y
        return RegularPoint(x3, y3)
    except ZeroDivisionError:
        return PointAtInfinity()


if __name__ == "__main__":
    # test adding two different points
    point3 = add_points(RegularPoint(GF(7), GF(2)), RegularPoint(GF(9), GF(4)))
    assert point3 == RegularPoint(GF(11), GF(7))

    # test adding same point
    point3 = add_points(RegularPoint(GF(5), GF(2)), RegularPoint(GF(5), GF(2)))
    assert point3 == RegularPoint(GF(7), GF(2))

    # test adding inverse point
    point3 = add_points(RegularPoint(GF(11), GF(7)), RegularPoint(GF(11), GF(6)))
    assert isinstance(point3, PointAtInfinity)

    # test adding point at infinity as a
    point = RegularPoint(GF(11), GF(6))
    point3 = add_points(PointAtInfinity(), point)
    assert point3 == point
    
    # test adding point at infinity as a
    point = RegularPoint(GF(11), GF(6))
    point3 = add_points(point, PointAtInfinity())
    assert point3 == point

    gen = RegularPoint(GF(5), GF(6))
    current = gen
    gen_point = False
    for x in range(20):
        current = add_points(current, gen)
        if current == gen:
            gen_point = True
            break
    assert gen_point
    