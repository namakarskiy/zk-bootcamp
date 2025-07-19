from py_ecc.bn128 import G1, G2, multiply

def print_g1_point(name, point, scalar):
    print(f"// {name} = {scalar} * G1")
    if point:
        print(f"G1Point memory {name} = G1Point({point[0]}, {point[1]});\n")
    else:
        print(f"G1Point memory {name} = G1Point(0, 0);\n")


def print_g2_point(name, point, scalar):
    print(f"// {name} = {scalar} * G2")
    print(f"G2Point memory {name} = G2Point({point[0].coeffs[1]}, {point[0].coeffs[0]}, {point[1].coeffs[1]}, {point[1].coeffs[0]});\n")


def print_constant_g1(name, point, scalar):
    print(f"// {name} = {scalar} * G1")
    print(f"uint256 {name}X = {point[0]};")
    print(f"uint256 {name}Y = {point[1]};\n")

def print_constant_g2(name, point, scalar):
    print(f"// {name} = {scalar} * G2")
    print(f"uint256 {name}X1 = {point[0].coeffs[1]};")
    print(f"uint256 {name}Y1 = {point[0].coeffs[0]};")
    print(f"uint256 {name}X2 = {point[1].coeffs[1]};")
    print(f"uint256 {name}Y2 = {point[1].coeffs[0]};\n")


def print_x(x1, x2, x3):
    print(f"uint256 x1 = {x1};")
    print(f"uint256 x2 = {x2};")
    print(f"uint256 x3 = {x3};\n")



# X1
x1 = 0
x2 = 0
x3 = 0
x1_scalar = x1+x2 +x3
X1 = multiply(G1, x1_scalar)

# A1
a1_scalar = -85
a1 = multiply(G1, abs(a1_scalar))

# B2
b2_scalar = 1
b2 = multiply(G2, b2_scalar)

# alfa1
alfa1_scalar = 5
alfa1 = multiply(G1, alfa1_scalar)

# beta2
beta2_scalar = 17
beta2 = multiply(G2, beta2_scalar)

# c1
c1_scalar = 0  
c1 = multiply(G1, c1_scalar)

# gamma2 
gamma2_scalar = 3
gamma2 = multiply(G2, gamma2_scalar)

# delta2
delta2_scalar = 7
delta2 = multiply(G2, delta2_scalar)

print("Will pass: ", a1_scalar * b2_scalar + alfa1_scalar * beta2_scalar + x1_scalar * gamma2_scalar + c1_scalar * delta2_scalar == 0)
print("=" * 80)


print_g1_point("A", a1, a1_scalar)
print_g2_point("B", b2, b2_scalar)
print_constant_g1("alfa", alfa1, alfa1_scalar)
print_constant_g2("beta", beta2, beta2_scalar)
print_constant_g2("gamma", gamma2, gamma2_scalar)
print_constant_g2("delta", delta2, delta2_scalar)
print_x(x1, x2, x3)
print_g1_point("C", c1, c1_scalar)



