import random
import numpy as np

def random_init_X(n):
    # Generate sensible random X

    sensible_range = int(n/5)

    # pick midprice
    # force midprice to be in middle of range
    p_m = random.randint(int(n/2 - sensible_range), int(n/2 + sensible_range))

    # pick sensible spread size
    p_s = 1 #random.randint(1,sensible_range)

    max_order_size = 1000
    orders = np.array( random.sample(range(max_order_size), 2*sensible_range) )

    bid_orders = -1 * orders[0:int(len(orders)/2)]
    ask_orders = orders[int(len(orders)/2):]

    X=np.zeros((n))
    X[p_m-sensible_range-p_s:p_m-p_s] = bid_orders
    X[p_m+p_s:p_m+sensible_range+p_s] = ask_orders
    return (X)

class UnknownPriceException(Exception):
    pass

def get_lambda(i):
    if i == 1:
        return 1.85
    elif i == 2:
        return 1.51
    elif i == 3:
        return 1.09
    elif i == 4:
        return 0.88
    elif i == 5:
        return 0.77
    else:
        raise UnknownPriceException('unknown i')

def get_theta(i):
    if i == 1:
        return 0.71
    elif i == 2:
        return 0.81
    elif i == 3:
        return 0.68
    elif i == 4:
        return 0.56
    elif i == 5:
        return 0.47
    else:
        raise UnknownPriceException('unknown i')

def get_mu():
    return 0.94

def get_k():
    return 1.92

def get_alpha():
    return 0.52

def get_best_ask_bid_order_num(X):
    [p_A_ind, p_B_ind] = get_best_ask_bid_ind(X)
    p_A = X[p_A_ind]
    p_B = X[p_B_ind]
    return [p_A, p_B]

def get_best_ask_bid_ind(X):
    p_A_ind = np.where(X>0)[0][0]
    p_B_ind = np.where(X<0)[0][-1]
    return [p_A_ind, p_B_ind]

# TODO: add admissibility check

def simulate_order_book(n_steps, X):
    # gibbs sampling with independent factors
    for step in range(n_steps):
        # limit buy order
        # x -> x^(p-1)
        [p_A_ind, p_B_ind] = get_best_ask_bid_ind(X)
        for p in range(p_A_ind):
            try:
                X[p] -= np.random.poisson(get_lambda(p))

                # buy orders can not be positive
                if X[p] > 0:
                    X[p] = 0
            except UnknownPriceException:
                pass

        # limit sell order
        # x -> x^(p+1)
        [p_A_ind, p_B_ind] = get_best_ask_bid_ind(X)
        for p in range(p_B_ind+1, len(X)):
            try:
                X[p] += np.random.poisson(get_lambda(p))

                # sell orders can not be negative
                if X[p] < 0:
                    X[p] = 0                
            except UnknownPriceException:
                pass

        # market buy order
        # x -> x^(p_B(t)+1)
        [p_A_ind, p_B_ind] = get_best_ask_bid_ind(X)
        X[p_A_ind] += np.random.poisson(get_mu())
        # sell orders can not be negative
        if X[p_A_ind] < 0:
            X[p_A_ind] = 0                

        # market sell order
        # x -> x^(p_A(t)-1)
        [p_A_ind, p_B_ind] = get_best_ask_bid_ind(X)
        X[p_B_ind] -= np.random.poisson(get_mu())
        # buy orders can not be positive
        if X[p] > 0:
            X[p] = 0

        # cancel limit buy order
        # x -> x^(p+1)
        [p_A_ind, p_B_ind] = get_best_ask_bid_ind(X)
        for p in range(p_A_ind):
            try:
                X[p] += np.random.poisson(get_theta(p)*abs(X[p]))

                # buy orders can not be positive
                if X[p] > 0:
                    X[p] = 0
            except UnknownPriceException:
                pass

        # cancel limit sell order
        # x -> x^(p+1)
        [p_A_ind, p_B_ind] = get_best_ask_bid_ind(X)
        for p in range(p_B_ind+1, len(X)):
            try:
                X[p] -= np.random.poisson(get_theta(p)*X[p])

                # sell orders can not be negative
                if X[p] < 0:
                    X[p] = 0
            except UnknownPriceException:
                pass

    return X
