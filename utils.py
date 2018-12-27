import random
import numpy as np
import json
import math

# TODO: add admissibility check

def random_init_X(n):
    # Generate sensible random X

    sensible_range = int(n/5)

    # pick midprice
    # force midprice to be in middle of range
    p_m = random.randint(int(n/2 - sensible_range), int(n/2 + sensible_range))

    # pick sensible spread size
    p_s = 1 #random.randint(1,sensible_range)

    min_order_size = 0
    max_order_size = 2
    orders = []
    for i in range(2*sensible_range):
        orders.append(int(random.random()*(max_order_size-min_order_size)+min_order_size))
    orders = np.array(orders)

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
        return 0.001
        # if i > 30:
        #     return 0.0001
        # else:
        #     return 0.77-((i-5)*((0.77-0.001)/25))
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
        return 0.001
        # if i > 30:
        #     return 0.0001
        # else:
        #     return 0.47-((i-5)*((0.47-0.001)/25))
        #raise UnknownPriceException('unknown i')


def get_mu():
    return 0.94


def get_k():
    return 1.92


def get_alpha():
    return 0.52


def get_mid_price(X):
    [p_A, p_B] = get_ask_bid_price(X)
    # rounding with int ok?
    return (p_A + p_B) / 2


def get_ask_bid_price(X):
    # returns best ask and bid price given state X
    # p_A and p_B are defined as indices of X
    p_A = np.where(X>0)[0][0]
    p_B = np.where(X<0)[0][-1]
    return [p_A, p_B]


def get_rates(X):
    # sum all possible event rates
    # TODO: convert nnz_rates to dictionary

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
    for relative_p in range(1, n-p_B):
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
        rate = get_theta(relative_p) * abs(X[p_A-relative_p])
        sum_rates += rate
        if rate:
            nnz_rates.append(('cancellimitbuy', p_A-relative_p, rate))

    # cancel limit sell order
    # x -> x^(p+1)
    for relative_p in range(1, n-p_B):
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

    new_state = state
    if event_type == 'limitbuy':
        assert state[event_price] <= 0, print_execution_error('limit buy orders must not arrive at positive quotes', event, state)
        new_state[event_price] -= order_size
    elif event_type == 'limitsell':
        assert state[event_price] >= 0, print_execution_error('limit sell orders must not arrive at negative quotes', event, state)
        new_state[event_price] += order_size
    elif event_type == 'marketbuy':
        assert state[event_price] > 0, print_execution_error('best ask price quotes must be positive', event, state)
        new_state[event_price] -= order_size
    elif event_type == 'marketsell':
        assert state[event_price] < 0, print_execution_error('best sell price quotes must be negative', event, state)
        new_state[event_price] += order_size
    elif event_type == 'cancellimitbuy':
        assert state[event_price] < 0, print_execution_error('cancel limit buy orders must not arrive at positive quotes', event, state)
        new_state[event_price] += order_size
    elif event_type == 'cancellimitsell':
        assert state[event_price] > 0, print_execution_error('cancel limit sell orders must not arrive at negative quotes', event, state)
        new_state[event_price] -= order_size
    else:
        raise Exception('programming error: unknown event_type for event: %s' %event)

    return new_state


def simulate_order_book(event_counter, initial_X):
    n = len(initial_X)
    state = initial_X
    state_str = json.dumps(list(initial_X))

    clock = 0
    all_states = {}
    Q_i = [0]*n
    Q_i_counter = 0

    limit_order_counter = 0
    cancel_limit_order_counter = 0
    market_order_counter = 0
    all_sum_rates = []
    all_taos = []
    p_m_current = get_mid_price(initial_X)
    volatility_price_change_num = 370
    RV = 0
    for event_index in range(event_counter):
        (sum_rates, nnz_rates) = get_rates(state)
        all_sum_rates.append(sum_rates)

        # pick next event time
        # tau = np.random.exponential(1/sum_rates)
        tau = 1/sum_rates * np.log(1/np.random.uniform())
        all_taos.append(tau)

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

        [p_A, p_B] = get_ask_bid_price(state)
        event_type = event[0]
        event_price = event[1]
        if event_type in ['limitbuy', 'cancellimitbuy']:
            best_quote = p_A
            assert best_quote > event_price, 'limitbuy or cancellimitbuy quote can not have price %s larger than best ask price %s event %s' %(event_price, p_A, event)
        elif event_type in ['limitsell', 'cancellimitsell']:
            best_quote = p_B
            assert best_quote < event_price, 'limitsell or cancellimitsell quote can not have price %s less than best bid price %s event %s' %(event_price, p_A, event)
        else:
            best_quote = None

        if event_type in ['cancellimitbuy', 'cancellimitsell']:
            cancel_limit_order_counter += 1
        elif event_type in ['limitbuy', 'limitsell']:
            limit_order_counter += 1
        elif event_type in ['marketbuy', 'marketsell']:
            market_order_counter += 1


        #sum should be in integer groups of tau
            
        if best_quote:
            #Q_i[abs(best_quote-event_price)] += abs(state[event_price])
            for i in range(1, 30):
                # number of buy orders at a distance i from the ask
                q_i_B = abs(state[p_A-i])
                # number of sell orders at a distance i from the bid
                q_i_A = state[p_B+i]

                #state_debug_str = ''
                # for s_i, s in enumerate(state):
                #     state_debug_str += '%s: %s\n' %(s_i, s)
                assert q_i_B >= 0 and q_i_A >= 0, 'q_i_A and q_i_B must be larger than zero! i %s p_A %s p_B %s q_i_B %s q_i_A %s event %s state %s' %(i, p_A, p_B, q_i_B,q_i_A,event, state)

                Q_i[i] += q_i_B+q_i_A
            Q_i_counter += 2

        state = execute_event(event, state)
        state_str = json.dumps(list(state))

        p_m_new = get_mid_price(state)
        if p_m_new != p_m_current:
            if volatility_price_change_num != 0:
                volatility_price_change_num -= 1
                RV += pow( np.log( p_m_new / p_m_current ), 2)
                p_m_current = p_m_new

        clock += tau

        if volatility_price_change_num == 0:
            print( 'volatility_price_change_num == 0 break event_index %s' %event_index )
            #break

    for q_i, q in enumerate(Q_i):
        Q_i[q_i] /= Q_i_counter # (limit_order_counter+cancel_limit_order_counter)

    print('limit_order_counter %s cancel_limit_order_counter %s market_order_counter %s' %(limit_order_counter, cancel_limit_order_counter, market_order_counter))
    print('all_sum_rates %s' %all_sum_rates)
    print('all_taos %s' %all_taos)
    print('volatility_price_change_num %s' %volatility_price_change_num)
    return (all_states, Q_i, np.sqrt(RV))
