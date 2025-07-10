# Use this resource as a reference for implementing the algorithm: https://cryptobook.nakov.com/digital-signatures/ecdsa-sign-verify-messages
# The following may also be helpful:

# https://www.rareskills.io/post/finite-fields
# https://www.rareskills.io/post/elliptic-curve-addition
# https://www.rareskills.io/post/elliptic-curves-finite-fields
# https://rareskills.io/post/ecdsa-tutorial

# Implement ECDSA from scratch. You want to use the secp256k1 curve (which specifies the values for the curve).
# When starting off, use the Elliptic curve multiplication library used in the blog post linked here: 
# https://www.rareskills.io/post/generate-ethereum-address-from-private-key-python

# 1) pick a private key
# 2) generate the public key using that private key (not the eth address, the public key)
# 3) pick message m and hash it to produce h (h can be though of as a 256 bit number)
# 4) sign m using your private key and a randomly chosen nonce k. produce (r, s, h, PubKey)
# 5) verify (r, s, h, PubKey) is valid

# You may use a library for point multiplication, but everything else you must do from scratch. Remember, when you compute the multiplicative inverse, you need to do it with respect to the curve order.
# Pay close attention to the distinction between the curve order and the prime number $p$ we compute the modulus of $y^2=x^3+b \pmod p$.

import hashlib
import hmac
from ecpy.curves import Curve, Point
from dataclasses import dataclass


# Extended Euclidean Algorithm
def _inverse(a: int, n: int) -> int:
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n


def _deterministic_generate_k(msghash: bytes, private_key: bytes, order: int) -> int:
    """
    Generate an RFC 6979-compliant deterministic `k` for ECDSA signatures.
    """
    v = b"\x01" * 32
    k = b"\x00" * 32
    k = hmac.new(k, v + b"\x00" + private_key + msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v + b"\x01" + private_key + msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()

    while True:
        # Generate candidate k
        v = hmac.new(k, v, hashlib.sha256).digest()
        candidate = int.from_bytes(v, "big")  # Convert bytes to int

        # RFC 6979 compliance check: must be in [1, n-1]
        if 1 <= candidate < order:
            return candidate

        # Regenerate k if candidate is invalid
        k = hmac.new(k, v + b"\x00", hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()


def _sha256_hash(message: str) -> bytes:
    message_bytes = message.encode("utf-8")
    hash_object = hashlib.sha256(message_bytes)
    return hash_object.digest()


@dataclass(frozen=True, slots=True)
class Signature:
    r: int
    s: int
    h: int
    pubkey: tuple[int, int]


def sign(message: str, private_key: bytes) -> Signature:
    curve = Curve.get_curve("secp256k1")
    msghash = _sha256_hash(message=message)
    pk_int = int.from_bytes(private_key, "big")
    k = _deterministic_generate_k(
        msghash=msghash, private_key=private_key, order=curve.order
    )
    R = curve.mul_point(k, curve.generator)
    r = R.x
    h = int.from_bytes(msghash, "big")
    s = (_inverse(k, curve.order) * (h + r * pk_int)) % curve.order
    pubkey = curve.mul_point(pk_int, curve.generator)
    return Signature(
        r=r,
        s=s,
        h=h,
        pubkey=(pubkey.x, pubkey.y),
    )


def verify(message: str, signature: Signature) -> bool:
    curve = Curve.get_curve("secp256k1")
    msghash = int.from_bytes(_sha256_hash(message=message))
    s1 = _inverse(signature.s, curve.order)
    part_a = curve.mul_point(msghash * s1, curve.generator)
    part_b = curve.mul_point(
        signature.r * s1,
        Point(signature.pubkey[0], signature.pubkey[1], curve=curve),
    )    
    R_verify = add_points(
        (part_a.x, part_a.y),
        (part_b.x, part_b.y),
        field=curve.field
    )
    return R_verify[0] == signature.r   


def add_points(a: tuple[int, int] | None, b: tuple[int, int] | None, field: int) -> tuple[int, int] | None:
    # Point at infinity represented as None here
    if a is None:
        return b
    if b is None:
        return a
    if a[1] + b[1] % field == 0:
        return None
    if a == b:
        def slope(point, _):
            return (3 * point[0] ** 2)  * _inverse(2 * a[1], field) % field  
    else:
        def slope(a: Point, b: Point) -> int: 
            return (b[1] - a[1]) * _inverse((b[0] -  a[0]), field) % field
    try:
        lmbd = slope(a, b)
        x3 = (lmbd ** 2 - a[0] - b[0]) % field
        y3 = (lmbd * (a[0] - x3) - a[1]) % field
        return (x3, y3)
    # in theory shouldn't happen, but added just in case
    except ZeroDivisionError:
        return None


if __name__ == "__main__":
    from pprint import pprint

    pk = b"0xdead"
    for message in ["elliptic", "curve", "ecdsa",]:
        signature = sign(message=message, private_key=pk)
        pprint(f"Message is {message}. {signature=}")
        print(f"Signature verified: {verify(message=message, signature=signature)} for {message}")
