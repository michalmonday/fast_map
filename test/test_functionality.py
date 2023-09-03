
from fast_map import fast_map
import time

def func(x):
    time.sleep(1)
    return x * x

for i in fast_map(func, range(8), threads_limit=100, procs_limit=2):
    print(i)
