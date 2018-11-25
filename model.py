import numpy as np
from utils import random_init_X
from utils import simulate_order_book
import random

n=20

random.seed(0)
np.random.seed(0)

X=random_init_X(n)

print(X)

all_states = simulate_order_book(pow(10,3), X)
all_tau = sum(all_states.values())
for state in all_states:
    print('state %s probability %s' %(state, all_states[state]/all_tau))

