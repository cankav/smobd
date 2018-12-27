from mpmath import *
from utils import get_lambda

INF = 10^6

def f_a_k():
    pass

def f_b_k():
    pass

def get_Phi(k):
    if k == INF:
        return f_a_k(S, k) / f_b_k(S, k)

    return f_a_k(S,k) / ( f_b_k(S, k) + get_Phi(k+1) )

def f_hat(S, j, s):
    result = (-1/get_lambda(S))**j
    for i in range(1, j+1):
        result *= get_Phi(i)

def fp(s):
    return (1/s * f_hat(S, a, s) ** f_hat(S, b, -s))

# implements eq 15
def p_increase_midprice_laplace(a, b, S):
    mp.dps = 15; mp.pretty = True
    return ( invertlaplace(fp,0.000001) ) # 0 results with division by zero error?

print(p_increase_midprice_laplace(1,1,1))
