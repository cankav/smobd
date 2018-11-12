import random
import numpy as np

def random_init_X(n):
    # Generate sensible random X

    sensible_range = int(n/5)

    # pick midprice
    # force midprice to be in middle of range
    p_m = random.randint(int(n/2 - sensible_range), int(n/2 + sensible_range))

    # pick sensible spread size
    p_s = random.randint(1,sensible_range)

    max_order_size = 1000
    orders = np.array( random.sample(range(max_order_size), 2*sensible_range) )

    bid_orders = -1 * orders[0:int(len(orders)/2)]
    ask_orders = orders[int(len(orders)/2):]

    X=np.zeros((n))
    X[p_m-sensible_range-p_s:p_m-p_s] = bid_orders
    X[p_m+p_s:p_m+sensible_range+p_s] = ask_orders
    return (X)

