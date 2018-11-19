import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)

current_value = 0
pp = [current_value,]

for i in range(25):
    current_value += np.random.poisson(0.5)
    pp.append(current_value)

# example:
# http://www.math.uchicago.edu/~may/VIGRE/VIGRE2010/REUPapers/Mcquighan.pdf page 8
plt.plot(pp)
plt.show()
