import random
import numpy as np
import json

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
        return 0.01
        #raise UnknownPriceException('unknown i')


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
        return 0.01
        #raise UnknownPriceException('unknown i')


def get_mu():
    return 0.94


def get_k():
    return 1.92


def get_alpha():
    return 0.52


def get_ask_bid_price(X):
    # returns best ask and bid price given state X
    # p_A and p_B are defined as indices of X
    p_A = np.where(X>0)[0][0]
    p_B = np.where(X<0)[0][-1]
    return [p_A, p_B]

# TODO: add admissibility check


def get_rates(X):
    # sum all possible event rates

    [p_A, p_B] = get_ask_bid_price(X)
    n = len(X)

    nnz_rates = []
    sum_rates = 0

    # limit buy order
    # x -> x^(p-1)
    for relative_p in range(1, p_A+1):
        rate = get_lambda(relative_p)
        sum_rates += rate
        if rate:
            nnz_rates.append(('limitbuy', p_A-relative_p, rate))

    # limit sell order
    # x -> x^(p+1)
    for relative_p in range(1, n-p_B-1):
        rate = get_lambda(relative_p)
        sum_rates += rate
        if rate:
            nnz_rates.append(('limitsell', p_B+relative_p, rate))

    # market buy order
    # x -> x^(p_A(t)+1)
    sum_rates += get_mu()
    nnz_rates.append(('marketbuy', p_A, get_mu()))

    # market sell order
    # x -> x^(p_B(t)-1)
    sum_rates += get_mu()
    nnz_rates.append(('marketsell', p_B, get_mu()))

    # cancel limit buy order
    # x -> x^(p+1)
    for relative_p in range(1, p_A+1):
        # can not issue cancel order unless there is existing limit order in p
        if abs(X[p_A-relative_p]):
            rate = get_theta(relative_p) * abs(X[p_A-relative_p])
            sum_rates += rate
            if rate:
                nnz_rates.append(('cancellimitbuy', p_A-relative_p, rate))

    # cancel limit sell order
    # x -> x^(p+1)
    for relative_p in range(1, n-p_B-1):
        # can not issue cancel order unless there is existing limit order in p
        if abs(X[p_B+relative_p]):
            rate = get_theta(relative_p) * abs(X[p_B+relative_p])
            sum_rates += rate
            if rate:
                nnz_rates.append(('cancellimitsell', p_B+relative_p, rate))

    return (sum_rates, nnz_rates)


def print_execution_error(error_str, event, state):
    [p_A, p_B] = get_ask_bid_price(state)
    return ('%s p_A %s p_B %s event %s state \n%s' %(error_str, p_A, p_B, event, state))

def execute_event(event, state, order_size=1):
    event_type = event[0]
    event_price = event[1]

    if event_type == 'limitbuy':
        assert state[event_price] <= 0, print_execution_error('limit buy orders must not arrive at positive quotes', event, state)
        state[event_price] -= order_size
    elif event_type == 'limitsell':
        assert state[event_price] >= 0, print_execution_error('limit sell orders must not arrive at negative quotes', event, state)
        state[event_price] += order_size
    elif event_type == 'marketbuy':
        assert state[event_price] > 0, print_execution_error('best ask price quotes must be positive', event, state)
        state[event_price] -= order_size
    elif event_type == 'marketsell':
        assert state[event_price] < 0, print_execution_error('best sell price quotes must be negative', event, state)
        state[event_price] += order_size
    elif event_type == 'cancellimitbuy':
        assert state[event_price] < 0, print_execution_error('cancel limit buy orders must not arrive at positive quotes', event, state)
        state[event_price] += order_size
    elif event_type == 'cancellimitsell':
        assert state[event_price] > 0, print_execution_error('cancel limit sell orders must not arrive at negative quotes', event, state)
        state[event_price] -= order_size
    else:
        raise Exception('programming error: unknown event_type for event: %s' %event)

    return state


def simulate_order_book(event_num, initial_X):
    n = len(initial_X)
    state = initial_X
    state_str = json.dumps(list(initial_X))

    clock = 0
    all_states = {}

    for event in range(event_num):
        (sum_rates, nnz_rates) = get_rates(state)

        # pick next event time
        tau = np.random.exponential(1/sum_rates)

        if state_str not in all_states:
            all_states[state_str] = tau
        else:
            all_states[state_str] += tau

        # pick next event type
        rand_event_p = np.random.uniform() * sum_rates
        event = None
        for nnz_rate in nnz_rates:
            rand_event_p -= nnz_rate[2]
            if rand_event_p <= 0:
                event = nnz_rate
                break

        assert event, 'event can not be none'

        state = execute_event(event, state)
        state_str = json.dumps(list(state))

        clock += tau

    return all_states
