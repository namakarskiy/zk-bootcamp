// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {console} from "forge-std/console.sol";

struct ECPoint {
    uint256 x;
    uint256 y;
}

contract Curve {
    uint256 public constant XG = 1;
    uint256 public constant YG = 2;
    uint256 public constant CURVE_ORDER = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;
    uint256 public constant FIELD_ORDER = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;

    function rationalAdd(ECPoint calldata A, ECPoint calldata B, uint256 num, uint256 den)
        public
        view
        returns (bool verified)
    {
        require(den != 0, "den is 0");
        uint256 multiplier = mulmod(num, modExp(den, CURVE_ORDER - 2, CURVE_ORDER), CURVE_ORDER);
        ECPoint memory expected = ecAdd(A, B);
        ECPoint memory actual = ecMul(ECPoint(XG, YG), multiplier);
        verified = expected.x == actual.x && expected.y == actual.y;
    }

    function matmul(uint256[] calldata matrix, uint256 n, ECPoint[] calldata s, uint256[] calldata o)
        public
        view
        returns (bool verified)
    {
        require(n > 0, "Matrix empty");
        require(matrix.length == n * n, "matrix != n * n");
        require(s.length == n, "s len is incorrect");
        require(o.length == n, "o len is incorrect");

        ECPoint[] memory actual = new ECPoint[](n);
        for (uint256 i = 0; i < n; i++) {
            ECPoint memory sum = ecMul(s[0], matrix[i * n]);
            for (uint256 j = 1; j < n; j++) {
                ECPoint memory tmp = ecMul(s[j], matrix[i * n + j]);
                sum = ecAdd(sum, tmp);
            }
            actual[i] = sum;
        }
        ECPoint memory gen = ECPoint(XG, YG);
        for (uint256 i = 0; i < n; i++) {
            ECPoint memory tmp = ecMul(gen, o[i]);
            if (tmp.x != actual[i].x || tmp.y != actual[i].y) {
                return false;
            }
        }
        verified = true;
    }

    function modExp(uint256 base, uint256 exp, uint256 mod) public view returns (uint256) {
        bytes memory precompileData = abi.encode(32, 32, 32, base, exp, mod);
        (bool ok, bytes memory data) = address(5).staticcall(precompileData);
        require(ok, "expMod failed");
        return abi.decode(data, (uint256));
    }

    function ecAdd(ECPoint memory a, ECPoint memory b) public view returns (ECPoint memory result) {
        bytes memory data = abi.encodePacked(a.x % FIELD_ORDER, a.y % FIELD_ORDER, b.x % FIELD_ORDER, b.y % FIELD_ORDER);
        (bool ok, bytes memory encoded) = address(6).staticcall(data);
        require(ok, "ecAdd failed");
        result = abi.decode(encoded, (ECPoint));
    }

    function ecMul(ECPoint memory point, uint256 scalar) public view returns (ECPoint memory result) {
        bytes memory data = abi.encodePacked(point.x % FIELD_ORDER, point.y % FIELD_ORDER, scalar);
        (bool ok, bytes memory encoded) = address(7).staticcall(data);
        require(ok, "ecMul failed");
        result = abi.decode(encoded, (ECPoint));
    }
}
