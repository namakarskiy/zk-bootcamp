# 1. Let our set be real numbers. Show a binary operator that is not closed
# division, divsion by zero is undefined

# 2. Find a binary operator that is closed but not associative for real numbers
# exponent, substraction, division


# 3. What algebraic structure (group, monoid, semigroup, etc) is all even integers under addition
# it's abelian group, 
#  a. it's closed as even num1 + even num2 = even num 3
#  b. it's assotiative a + (b + c) = (a + b) + c
#  c. identity is 0, which is even
#  d. have inverse which is -num
#  e. it's commutative a + b = b + a


# 4. What algebraic structure is all odd integers under multiplication?
# it's monoid
#  a. it's closed
#  b. it's assotiative
#  c. identity is 1
#  d. not all elements have inverse

# 5. Let our set be 3 x 2 matrices of integers under addition. What algebraic structure is this?
# it's abelian group
#  a. it's closed
#  b. it's assotiative
#  c. identity is 0 matrix
#  d. all elements have inverse which -M
#  e. it's commutative


# 6. Suppose our set is all rational numbers $\mathbb{Q}$ except $0$ and our binary operator is division. What algebraic structure is this?
# it's magma, or if be more precise it's quasigroup, because a / x = b and y / a = b raise unique solutions 
#  a. it's closed, because zero is not included
#  b. it's not assotiative a / (b / c) != (a / b ) /c


# 7. Suppose our set is 𓅔 (a) 𓆓 (b)  **𓆟** (c)
#     1. Define a binary operator that makes it a group. You can define the binary operator’s property by constructing a table where the left two columns are the inputs and the right column is the result. Remember you need to allow that the inputs can be the same, for example (𓅔,𓅔) —> ?
#     sum modulo 3, because we can map each element to a member of set, let's say {0,1,2} which is a group
#
#     2. Define a binary operator that makes it *not* a group (but it should be closed). Hint: if there is no identity element, then it is not a group
#       we can pick one element as result for all oprations, in that case all combinations of a,b,c wiil give a. a will have identity, but b X b, 
#       or c x c would not. Which will make it a magma


# 8. What is the size of the smallest possible group? (Remember, a group is a set, so this is asking how large the set is)
# it's 1, for example {0} under addtion
#  a. it's closed  0 + 0  = 0
#  b. it's assotiative 0 + (0 + 0) = (0 + 0) + 0
#  c. identity is 0
#  d. have inverse which is 0
