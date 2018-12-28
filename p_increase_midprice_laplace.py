from mpmath import *
from utils import get_lambda
from utils import get_mu
from utils import get_theta
import sys
sys.setrecursionlimit(11000)

INF = 10*6

# implements eq 15
def p_increase_midprice_laplace(a, b, S):
    def a_n(k):
        return( -get_lambda(S) * (get_mu()+k*get_theta(S)) )

    def b_n(k, s):
        return( get_lambda(S)+get_mu()+k*get_theta(S)+s )

    def Phi(k, s):
        if k == INF:
            u = 0
        else:
            u = Phi(k+1, s)

        return ( a_n(k) / ( b_n(k, s) + u ) )

    # eq 18
    def f_hat(j, s):
        result = (-1/get_lambda(S))**j
        for i in range(1, j+1):
            result *= Phi(i, s)
        return (result)

    # eq 20
    def fp(s):
        return (1/s * f_hat(a, s) * f_hat(b, -s))

    mp.dps = 15; mp.pretty = True
    return ( invertlaplace(fp,0.0001) ) # 0 results with division by zero error?

print(p_increase_midprice_laplace(1,10,1))
