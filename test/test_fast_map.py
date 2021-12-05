import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

from fast_map import fast_map#, fast_map_simple


def io_and_cpu_expensive_blocking_function(x):
    time.sleep(1)
    for i in range(10 ** 6):
        pass
    return x

# def get_fast_map_simple(numbers, workers, func):
#     gen_obj = fast_map_simple(func, numbers, threads_limit=workers)
#     for i in gen_obj:
#         pass

def get_fast_map(numbers, workers, func):
    gen_obj = fast_map(func, numbers, threads_limit=workers)
    for i in gen_obj:
        pass

def get_ThreadPoolExecutor(numbers, workers, func):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        gen_obj = executor.map(func, numbers)
        # gen_obj = {executor.submit(wait_and_square, num): num for num in numbers}
    for i in gen_obj:
        pass

def get_ProcessPoolExecutor(numbers, workers, func):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        gen_obj = executor.map(func, numbers)
    for i in gen_obj:
        pass

def display(labels, results):
    #labels = ['G1', 'G2', 'G3', 'G4', 'G5']
    #men_means = [20, 34, 30, 35, 27]
    #women_means = [25, 32, 34, 20, 25]

    x = np.arange(len(labels))  # the label locations
    width = 0.25 # the width of the bars

    fig, ax = plt.subplots()
    rects = []
    print(labels, results)
    width_to_add = 0
    for name, durations in results.items():
        rects.append( ax.bar(x - width + width_to_add, durations, width, label=name) )
        width_to_add += width

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Duration')
    ax.set_xlabel('Number of tasks (each having its own worker to achieve full concurency)')
    ax.set_title('Performance comparison')
    ax.set_xticks(x, labels)
    ax.legend(loc='upper left')

    for rect in rects:
        ax.bar_label(rect, fmt='%.1f', padding=3)

    fig.tight_layout()

    plt.show()


def input_types_tests():
    def t_single(a):
        return a**a
    def t_multi(a, b):
        return a+b
    def t_str_single(a):
        return a
    def t_str_multi(a, b):
        return '|'.join([a,b])
    def t_list(a):
        return '|'.join([str(s) for s in a])
        
    for i in fast_map(t_single, [1,2,3,4]):
        print(i)
    for i in fast_map(t_multi, (1,2), (3,4)):
        print(i)
        
    for i in fast_map(t_str_multi, ('abc', 'efg'), ('a', 'b')):
        print(i)
    for i in fast_map(t_str_single, ['abc', 'efg', 'a', 'b']):
        print(i)
    for i in fast_map(t_single, range(10)):
        print(i)
    for i in fast_map(t_list, ([1,2,3],)):
        print(i)

if __name__ == '__main__':
    
        funcs = {
            'ThreadPoolExecutor'  : get_ThreadPoolExecutor,
            'ProcessPoolExecutor' : get_ProcessPoolExecutor,
            'fast_map' : get_fast_map
            #'fast_map_simple': get_fast_map_simple,
            }

        results = {name:[] for name in funcs.keys()} 
        labels = []
        
        for i in range(20, 30): 
        # for i in range(20, 21): 
        # for i in range(1,6): 
            workers = int(i**(i*0.08))
            numbers = range(workers)
            labels.append( f'{workers}' ) 
            print('workers =', workers)

            for j, (name, func) in enumerate(funcs.items()):

                start_time = time.time()
                # ProcessPoolExecutor fails at around 1000 workers but takes significant amount
                # of time before raising exception (it also affects further tests).
                # So condition below is used.
                if workers > 1000 and func == get_ProcessPoolExecutor:
                    duration = -1
                else: 
                    try:
                        func(numbers, workers, io_and_cpu_expensive_blocking_function)
                        duration = time.time() - start_time
                    except Exception as e:
                        print(e)
                        duration = -1
                results[name].append( duration )
                print(name, 'finished in:', duration)
                print()

        display(labels, results)



