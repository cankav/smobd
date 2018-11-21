import numpy as np

EVENT_NUM=100000

state = 0

# birth rate
lam = 2

# death rate
mu = 3

clock = 0

all_states = {}

for event in range(EVENT_NUM):
    if state == 0:
        # no death transition possible when state = 0
        sum_rates = lam
    else:
        sum_rates = mu+lam
    
    # pick next event time
    tau = np.random.exponential(1/sum_rates)

    if state not in all_states:
        all_states[state] = tau
    else:
        all_states[state] += tau

    # pick next event type
    if np.random.uniform() < (lam/sum_rates):
        #birth
        state += 1
    else:
        #death
        state -= 1

    clock += tau

print(all_states)

all_tau = sum(all_states.values())

for state in all_states:
    print('state %s probability %s' %(state, all_states[state]/all_tau))
