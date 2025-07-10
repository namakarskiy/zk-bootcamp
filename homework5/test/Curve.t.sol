// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {Curve, ECPoint} from "../src/Curve.sol";
import {console} from "forge-std/console.sol";

contract CurveTest is Test {
    Curve public curve;

    function setUp() public {
        curve = new Curve();
    }

    function testFuzz_AddPoints(uint256 a, uint256 b, uint256 den1, uint256 den2) public view {
        uint256 curve_order = curve.CURVE_ORDER();
        vm.assume(a < curve_order);
        vm.assume(b < curve_order);
        vm.assume(den1 > 0);
        vm.assume(den2 > 0);

        uint256 den1_inverse = curve.modExp(den1, curve_order - 2, curve_order);
        uint256 den2_inverse = curve.modExp(den2, curve_order - 2, curve_order);
        ECPoint memory aP = curve.ecMul(ECPoint(curve.XG(), curve.YG()), mulmod(a, den1_inverse, curve_order));
        ECPoint memory bP = curve.ecMul(ECPoint(curve.XG(), curve.YG()), mulmod(b, den2_inverse, curve_order));
        uint256 num = addmod(mulmod(a, den2, curve_order), mulmod(b, den1, curve_order), curve_order);
        uint256 den = mulmod(den1, den2, curve_order);
        assert(curve.rationalAdd(aP, bP, num, den));
    }

    function test_zero_a_b() public view {
        ECPoint memory aP = ECPoint(0, 0);
        ECPoint memory bP = ECPoint(0, 0);
        assert(curve.rationalAdd(aP, bP, 0, 100500));
    }

    function test_zero_with_point_at_infinity() public view {
        ECPoint memory aP = ECPoint(0, 0);
        ECPoint memory bP = curve.ecMul(ECPoint(curve.XG(), curve.YG()), 5);
        assert(curve.rationalAdd(aP, bP, 5, 1));
    }

    function test_matmul() public view {
        uint256 n = 3;
        // multipliers [1,2,3]
        uint256[] memory multipliers = buildMultipliers(n);
        //matrix [1,2,3,4,5,6,7,8,9]
        uint256[] memory matrix = buildMatrix(n * n);
        // s vector [P,Q,R]
        ECPoint[] memory s = buildPoints(multipliers);
        // build vector O
        uint256[] memory o = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            uint256 sum = 0;
            for (uint256 j = 0; j < n; j++) {
                sum += matrix[i * n + j] * multipliers[j];
            }
            o[i] = sum;
        }
        bool result = curve.matmul(matrix, n, s, o);
        assert(result);
    }

    function test_matmul_incorrect_n() public {
        uint256 n = 3;
        uint256[] memory multipliers = buildMultipliers(n);
        uint256[] memory matrix = buildMatrix(n * n);
        ECPoint[] memory s = buildPoints(multipliers);

        vm.expectRevert();
        curve.matmul(matrix, n + 100, s, multipliers);
    }

    function test_matmul_n_is_zero() public {
        uint256 n = 3;
        uint256[] memory multipliers = buildMultipliers(n);
        uint256[] memory matrix = buildMatrix(n * n);
        ECPoint[] memory s = buildPoints(multipliers);

        vm.expectRevert();
        curve.matmul(matrix, 0, s, multipliers);
    }

    function test_matmul_vector_lenght_is_incorrect() public {
        uint256 n = 3;
        uint256[] memory multipliers = buildMultipliers(n + 1);
        uint256[] memory matrix = buildMatrix(n * n);
        ECPoint[] memory s = buildPoints(multipliers);

        vm.expectRevert();
        curve.matmul(matrix, 0, s, multipliers);
    }

    function test_matmul_o_vector_lenght_is_incorrect() public {
        uint256 n = 3;
        uint256[] memory multipliers = buildMultipliers(n);
        uint256[] memory o = buildMultipliers(n + 1);
        uint256[] memory matrix = buildMatrix(n * n);
        ECPoint[] memory s = buildPoints(multipliers);

        vm.expectRevert();
        curve.matmul(matrix, 0, s, o);
    }

    function buildMultipliers(uint256 n) private pure returns (uint256[] memory multipliers) {
        multipliers = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            multipliers[i] = i + 1;
        }
    }

    function buildMatrix(uint256 n) private pure returns (uint256[] memory matrix) {
        matrix = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            matrix[i] = i + 1;
        }
    }

    function buildPoints(uint256[] memory multipliers) private view returns (ECPoint[] memory s) {
        ECPoint memory gen = ECPoint(curve.XG(), curve.YG());
        s = new ECPoint[](multipliers.length);
        for (uint256 i = 0; i < multipliers.length; i++) {
            s[i] = curve.ecMul(gen, multipliers[i]);
        }
    }
}
