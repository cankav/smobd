import numpy as np
from utils import random_init_X
from utils import simulate_order_book
import random
import matplotlib.pyplot as plt
import sys
import json

n=400

random.seed(0)
np.random.seed(0)

X=random_init_X(n)
#X=np.zeros((n))

print(X)

(all_states, Q_i) = simulate_order_book(pow(10,4), X)
all_tau = sum(all_states.values())

states_with_highest_p_num = 5
states_with_highest_p = [(0,0)]*states_with_highest_p_num

for state in all_states:
    print('state %s probability %s' %(state, all_states[state]/all_tau))

    if states_with_highest_p[0][1] < all_states[state]/all_tau:
        states_with_highest_p.pop()
        states_with_highest_p.insert( 0, (state, all_states[state]/all_tau) )

    # state = np.array(json.loads(state))

print('Q_i %s' %Q_i)

print('states_with_highest_p')
for s in states_with_highest_p:
    print(s)
sys.stdout.flush()

plt.plot(range(1,len(Q_i)), Q_i[1:])
plt.title('average number of orders')

plt.show()

