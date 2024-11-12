import atexit
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import math
from functools import partial
from threading import Thread
# import psutil

def cleanup_subprocesses(subprocesses):
    '''Cleanup running subprocesses on exit'''
    for subprocess in subprocesses:
        if subprocess.pid is None:
            continue
        else:
            subprocess.terminate()

def process_chunk(proc_id, func, threads_count, task_queue, result_queue):
    '''This is the target function for each spawned process. It receives 
    the task_queue where each task contains a collection of arguments for
    the function "func". '''
    # print('start proc id', proc_id, ' cpu core=', psutil.Process().cpu_num())
    def on_completed(future, index):
        res = future.result()
        # print('on_completed, res=', res)
        result_queue.put((index, res))
    with ThreadPoolExecutor(max_workers=threads_count) as executor:
        while True:
            i, task = task_queue.get()
            task_queue.task_done()
            if task is None:
                break
            future = executor.submit(func, *task)
            future.add_done_callback(partial(on_completed, index=i))
    # print('end proc id', proc_id, ' cpu core=', psutil.Process().cpu_num())

def calculate_procs_and_threads_per_process(threads_limit, procs_limit,
                                            tasks_count):
    '''This function returns a tuple containing:
    - the number of processes to spawn
    - the number of threads to spawn in each process
    threads_limit = total threads limit (e.g. if equal to 8 then on a 4 core
    cpu, 2 threads will be spawned in each process) 
    '''
    procs_count = mp.cpu_count()
    # Limit the number of processes
    if procs_limit:
        procs_count = min(procs_count, procs_limit)
    if tasks_count < procs_count:
        return tasks_count, 1
    if threads_limit and threads_limit < procs_count:
        return threads_limit, 1

    # Threads per process
    threads_pp = math.ceil(tasks_count / procs_count)
    if threads_limit:
        threads_pp = min(threads_pp, math.ceil(threads_limit/procs_count))
    # print("threads_pp =", threads_pp)
    return procs_count, threads_pp


def fast_map(f, *f_args, threads_limit=None, procs_limit=None):
    ''' This function works like the built-in map() function, but it spawns
    multiple processes and threads to speed up the execution.
    f_args = a collection of arguments for the function "f", using the same
    format as the original map function.
    threads_limit = total threads limit (e.g. if equal to 8, then on a 4 core
    cpu, 2 threads will be spawned in each process) '''
    if threads_limit is not None:
        assert threads_limit > 0, "threads_limit must be > 0"
    if procs_limit is not None:
        assert procs_limit > 0, "procs_limit must be > 0"

    def enqueuer(task_queues, f_args):
        ''' This function evenly enqueues tasks into 
        multiple task queues (one queue per process). '''
        for i, val in enumerate(zip(*f_args)):
            task_queues[i % len(task_queues)].put((i,val))
        for q in task_queues:
            q.put((None,None))

    # "task" is a single execution of the target 
    # function with specified arguments.
    tasks_count = len(f_args[0])
    procs_count, threads_pp = calculate_procs_and_threads_per_process(
        threads_limit, procs_limit, tasks_count)

    # Multiple task queues are used for the sake of 
    # even task distribution within processes.
    task_queues = [mp.JoinableQueue() for _ in range(procs_count)]
    result_queue = mp.Queue()

    procs = []

    # Clean up subprocesses on exit
    atexit.register(cleanup_subprocesses, procs)

    for i in range(procs_count):
        p = mp.Process(target=process_chunk, args=[
            i, f, threads_pp, task_queues[i], result_queue])
        procs.append(p)
        p.start()

    # Enqueue tasks (destination function arguments "f_args")
    # into multiple task queues.
    Thread(target=enqueuer, daemon=True, args=[task_queues, f_args]).start()

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
            while ordered_results.get(expected_index, None) is not None:
                yield ordered_results.pop(expected_index)
                expected_index += 1
            if expected_index == tasks_count:
                return

if __name__ == '__main__':
    pass
