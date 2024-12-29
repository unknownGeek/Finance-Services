import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ax =plt.gca()
# data = [{'x' : 1, 'y' : 2}, {'x' : 2, 'y' : 2}, {'x' : 3, 'y' : -1}, {'x' : 4, 'y' : 8},  {'x' : 10, 'y' : -80},  {'x' : 50, 'y' : 1000}]
data = pd.DataFrame(np.random.rand(10, 4), columns=['a', 'b', 'c', 'd'])
sales = pd.DataFrame(data)
sales.plot(kind='line', ax=ax)
ax.set_xlabel('X values')
ax.set_ylabel('Y values')
plt.title('Demo graph for Line plots')
plt.show()