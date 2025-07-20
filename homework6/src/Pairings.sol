// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {console} from "forge-std/console.sol";

struct G1Point {
    uint256 x;
    uint256 y;
}

struct G2Point {
    uint256 x1;
    uint256 y1;
    uint256 x2;
    uint256 y2;
}

contract Pairings {
    // alfa = 5 * G1
    G1Point _alfa =
        G1Point(
            10744596414106452074759370245733544594153395043370666422502510773307029471145,
            848677436511517736191562425154572367705380862894644942948681172815252343932
        );

    // beta = 17 * G2
    G2Point _beta =
        G2Point(
            15577308679414974642168536368096450326086203870944559758314800234684337462316,
            5571996575954125260736435753480252954196528247617148060558631406349160775832,
            3949072583587836530885517791345259776526014207612010591436388615095276192789,
            11302850696403459405052467769487663388868168369318255751101607320138145101673
        );

    // gamma = 3 * G2
    G2Point _gamma =
        G2Point(
            7273165102799931111715871471550377909735733521218303035754523677688038059653,
            2725019753478801796453339367788033689375851816420509565303521482350756874229,
            957874124722006818841961785324909313781880061366718538693995380805373202866,
            2512659008974376214222774206987427162027254181373325676825515531566330959255
        );

    // delta = 7 * G2
    G2Point _delta =
        G2Point(
            18551411094430470096460536606940536822990217226529861227533666875800903099477,
            15512671280233143720612069991584289591749188907863576513414377951116606878472,
            1711576522631428957817575436337311654689480489843856945284031697403898093784,
            13376798835316611669264291046140500151806347092962367781523498857425536295743
        );

    G1Point _g = G1Point(1, 2);

    uint256 _field_order =
        0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;
    uint256 _curve_order =
        0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;

    function verify(
        G1Point calldata A,
        G2Point calldata B,
        G1Point calldata C,
        uint256 x1,
        uint256 x2,
        uint256 x3
    ) public view returns (bool verified) {
        validateG1Point(A);
        validateG2Point(B);
        validateG1Point(C);
        // calculate X
        uint256 xScalar = addmod(
            x3,
            addmod(x1, x2, _curve_order),
            _curve_order
        );
        G1Point memory X = ecMul(_g, xScalar);
        bytes memory payload = abi.encode(
            negate(A),
            B,
            _alfa,
            _beta,
            X,
            _gamma,
            C,
            _delta
        );
        (bool result, bytes memory data) = address(8).staticcall(payload);
        require(result, "pairing failed");
        verified = abi.decode(data, (bool));
    }

    function negate(G1Point memory point) public view returns (G1Point memory) {
        uint256 neg_y = _field_order - (point.y % _field_order);
        point.y = neg_y;
        return point;
    }

    function ecMul(
        G1Point memory point,
        uint256 scalar
    ) public view returns (G1Point memory result) {
        bytes memory data = abi.encodePacked(point.x, point.y, scalar);
        (bool ok, bytes memory encoded) = address(7).staticcall(data);
        require(ok, "ecMul failed");
        result = abi.decode(encoded, (G1Point));
    }

    function validateG1Point(G1Point memory point) private view {
        require(point.x <= _field_order, "G1: x > field_order");
        require(point.y <= _field_order, "G1: y > field_order");
    }

    function validateG2Point(G2Point memory point) private view {
        require(point.x1 <= _field_order, "G2: x1 > field_order");
        require(point.y1 <= _field_order, "G2: y1 > field_order");
        require(point.x2 <= _field_order, "G2: x2 > field_order");
        require(point.y2 <= _field_order, "G2: y2 > field_order");
    }
}
