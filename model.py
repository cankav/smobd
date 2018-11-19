import numpy as np
from utils import random_init_X
from utils import simulate_order_book
import random

n=50

random.seed(0)
np.random.seed(0)

X=random_init_X(n)

print(X)

print(simulate_order_book(100, X))
