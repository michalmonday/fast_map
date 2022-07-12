''' It's my first python package.
    You may notice it's somewhat not very presentable for public release.
    But it seems to do the thing. '''

import multiprocessing as mp
# from multiprocessing.dummy import Pool as ThreadPool
from concurrent.futures import ThreadPoolExecutor
import math
# from itertools import repeat
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

def calculate_procs_and_threads_per_process(threads_limit, tasks_count):
    ''' threads_limit = total threads limit (e.g. if equal to 8 then on a 4 core
        cpu, 2 threads will be spawned in each process) '''
    procs_count = mp.cpu_count()
    if tasks_count < procs_count:
        procs_count = tasks_count
    if threads_limit and threads_limit < procs_count:
        procs_count

    # chunk to be processed by a single process
    chunk_size = math.ceil(tasks_count / procs_count)
    threads_pp = chunk_size # threads per process
    if threads_limit:
        threads_pp = min(threads_pp, math.ceil(threads_limit/procs_count))
    # print("threads_pp =", threads_pp)
    return procs_count, threads_pp

        


def fast_map(f, *v, threads_limit=None, forced_procs_count=None):
    ''' threads_limit = total threads limit (e.g. if equal to 8 then on a 4 core
        cpu, 2 threads will be spawned in each process) '''
    def enqueuer(queues, values, none_count):
        for i, val in enumerate(zip(*values)):
            # print('enqueue', i, val)
            queues[i % len(queues)].put((i,val))
        for q in queues:
            q.put((None,None))

    tasks_count = len(v[0])
    procs_count, threads_pp = calculate_procs_and_threads_per_process( threads_limit, tasks_count )

    # forced_procs_count is just for testing (not indended to be a feature)
    if forced_procs_count:
        procs_count = forced_procs_count

    task_queues = [mp.JoinableQueue() for _ in range(procs_count)] # multiple queues for the sake of even distribution
    result_queue = mp.Queue()

    procs = []
    for i in range(procs_count):
        p = mp.Process(target=process_chunk, args=[i, f, threads_pp, task_queues[i], result_queue]) 
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
            if expected_index == tasks_count:
                return

if __name__ == '__main__':
    pass
