from fast_map import fast_map
from threading import Thread, Lock
import time


def f(x):
    global lock_G
    print('f entered with x =', x)
    with lock_G:
        print('lock_G was acquired, x =', x)
        time.sleep(1)
    return x

def release_lock_after_delay(lock):
    time.sleep(1)
    lock.release()

lock_G = Lock()
lock_G.acquire()
# Thread(target=release_lock_after_delay, daemon=True, args=[lock_G]).start()
gen = fast_map(f, range(3))
time.sleep(1)
print('releasing lock')
lock_G.release()
for i in gen:
    print(i)
print('checking global lock (will not recognize that the lock is released)')
for i in fast_map(f, range(3)):
    print(i)
print('global lock done')

