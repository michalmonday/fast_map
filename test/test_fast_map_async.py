from fast_map import fast_map_async
import time

# task function is called from different processes/threads.
# Meaning that using threading.Lock objects inside it may
# lead to a deadlock if the default process creating method
# happens to be "fork" (instead of "spawn" or "forkserver")
def task(x):
    time.sleep(1)
    return x*x

# 2 callback functions below are called from the same process 
# (but a separate thread). Meaning that threading.lock objects
# can be safely used in here.
def on_result(result):
    print(result)

def on_done():
    print('all done')

# Returns threading.Thread object
t = fast_map_async(
        task,
        range(8), # argument list to tasks
        on_result = on_result,
        on_done = on_done,
        threads_limit = 100
        )

# Returned thread may be used to "t.join()" if we want
# to wait until all tasks are done. However the whole 
# point of using "fast_map_async" instead of "fast_map"
# is to continue execution.
t.join()
print()


# function that prints instead of returning
def task2(x):
    time.sleep(1)
    print(x*x)

# when we're not interested in return we may omit the on_result callback
# when we're not interested in knowing when all tasks got processed we may omit the on_done callback
t2 = fast_map_async(
        task2,
        range(8), # argument list to tasks
        threads_limit = 100
        )

t2.join()
print('all done 2')
