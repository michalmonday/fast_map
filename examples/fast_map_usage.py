from fast_map import fast_map
import time

# this function is called from different processes/threads.
# Meaning that using threading.Lock objects inside it may
# lead to a deadlock if the default process creating method
# happens to be "fork" (instead of "spawn" or "forkserver")
def io_and_cpu_expensive_function(x):
    time.sleep(1)
    for i in range(10 ** 4):
        pass
    return x*x

print('Unlimited threads (threads_count = number of tasks)')
# 8 threads in total will be used.
# On 4 core CPU, 2 threads will be spawned in each process.
for i in fast_map(io_and_cpu_expensive_function, range(8), threads_limit=None):
    print(i)
print('\n')

print('Threads limited to 4 (task will take 2 seconds instead of 1)')
# 8 threads in total will be used.
# On 4 core cpu, 1 thread will be spawned in each process.
for i in fast_map(io_and_cpu_expensive_function, range(8), threads_limit=4):
    print(i)
print('\n')


def task_with_multiple_params(a, b):
    return a + ' - ' + b

print('Using function with multiple parameters:')
for s in fast_map(task_with_multiple_params, ['apple', 'banana', 'cherry'], ['orange', 'lemon', 'pineapple']):
    print(s)
