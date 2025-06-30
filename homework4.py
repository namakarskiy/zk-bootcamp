# Use this resource as a reference for implementing
# the algorithm: https://cryptobook.nakov.com/digital-signatures/ecdsa-sign-verify-messages
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
    R_verify = curve.add_point(
        curve.mul_point(msghash * s1, curve.generator),
        curve.mul_point(
            signature.r * s1,
            Point(signature.pubkey[0], signature.pubkey[1], curve=curve),
        ),
    )
    return R_verify.x == signature.r


if __name__ == "__main__":
    from pprint import pprint

    pk = b"0xdead"
    for message in ["elliptic", "curve", "ecdsa",]:
        signature = sign(message=message, private_key=pk)
        pprint(f"Message is {message}. {signature=}")
        print(f"Signature verified: {verify(message=message, signature=signature)} for {message}")
