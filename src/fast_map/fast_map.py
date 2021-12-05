''' It's my first python package.
    You may notice it's somewhat not very presentable for public release.
    But it seems to do the thing. '''

import multiprocessing as mp
# from multiprocessing.dummy import Pool as ThreadPool
from concurrent.futures import ThreadPoolExecutor
import math
from itertools import repeat
from functools import partial
from threading import Thread
import time
# import psutil

def process_chunk(proc_id, f, threads_count, task_queue, result_queue):
    # print('start proc id', proc_id, ' cpu core=',psutil.Process().cpu_num())
    futures = []
    def on_completed(future, index):
        res = future.result()
        # print('on_completed, res=', res)
        result_queue.put((index, res))
    with ThreadPoolExecutor(max_workers=threads_count) as executor:
        while True:
            i, item = task_queue.get()
            task_queue.task_done()
            if item == None:
                break
            future = executor.submit(f, *item)
            future.add_done_callback(partial(on_completed, index=i))
    # print('end proc id', proc_id, ' cpu core=', psutil.Process().cpu_num())


def fast_map(f, *v, procs_limit=None, threads_limit=None, ordered=True):
    ''' Only ordered mode is available now. '''
    def enqueuer(queues, values, none_count):
        for i, val in enumerate(zip(*values)):
            # print('enqueue', i, val)
            queues[i % len(queues)].put((i,val))
        for q in queues:
            q.put((None,None))
    procs_count = mp.cpu_count()
    if procs_limit:
        procs_count = min(procs_limit, procs_count)

    # chunk to be processed by a single process
    chunk_size = math.ceil(len(v[0]) / procs_count)
    threads_count = chunk_size 
    if threads_limit:
        threads_count = min(threads_count, math.ceil(threads_limit/procs_count))
    # print("threads_count =", threads_count)

    task_queues = [mp.JoinableQueue() for _ in range(procs_count)] # multiple queues for the sake of even distribution
    result_queue = mp.Queue()

    procs = []
    for i in range(procs_count):
        p = mp.Process(target=process_chunk, args=[i, f, threads_count, task_queues[i], result_queue]) 
        procs.append(p)
        p.start()

    Thread(target=enqueuer, daemon=True, args=[task_queues, v, procs_count]).start()

    expected_index = 0
    ordered_results = {} # key=index val=result
    while True:
        alive_procs = [p for p in procs if p.is_alive()]
        if result_queue.empty() and len(alive_procs) == 0:
            return
        while not result_queue.empty():    
            i, res = result_queue.get()
            if i != expected_index:
                ordered_results[i] = res
                continue
            yield res
            expected_index += 1
            while ordered_results.get(expected_index, None):
                yield ordered_results.pop(expected_index)
                expected_index += 1
            if expected_index == len(v[0]):
                return

if __name__ == '__main__':
    pass
