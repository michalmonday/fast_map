## List of contents
* [Characteristics of fast\_map function](#characteristics-of-fast-map-function)  
* [Usage](#usage)  
* [Performance comparison](#performance-comparison) (against multithreading/multiprocessing on their own)   
* [Installation](#installation)  
* [Troubleshooting and issues](#troubleshooting-and-issues)  
* [Considerations](#considerations)  


## Characteristics of fast\_map function
* provides parallelism and concurrency for blocking functions    
* returns a [generator](https://stackoverflow.com/a/70233705/4620679) (meaning that individual returned values are returned immediately after being computed, before the whole collection is returned as a whole)  
* return is ordered (accordingly to supplied arguments)  
* uses the number of processes equal to CPU cores   
* uses the number of threads equal to the number of supplied tasks (unless threads\_limit argument is provided)  
* evenly distributes tasks within processes/threads  


## Usage
```python
from fast_map import fast_map
import time

def io_and_cpu_expensive_function(x):
    time.sleep(1)
    for i in range(10 ** 5):
        pass
    return x*x

# It will spawn 8 threads in total.
# On a 4-core CPU it will spawn 4 processes and 2 threads in each process.
for i in fast_map(io_and_cpu_expensive_function, range(8), threads_limit=None):
    print(i)
```

See [basic\_usage.py](./examples/basic_usage.py) for a more elaborated demonstration.  

## Performance comparison
I compared it against using muliprocessing/multithreading on their own. [test\_fast\_map.py](./test/test_fast_map.py ) is the script I used. It was tested with:  
  
Python3.7  
Ubuntu 18.04.6  
Intel i5-3320M   
8GB DDR3 memory


#### Comparison when using 10\*\*5 loops within the blocking function.
"-1" means that ProcessPoolExecutor failed due to "too many files open".  

![comparison image didn't show](./images/comparison.png)  


#### Comparison when using 10\*\*6 loops within the blocking function.  
"-1" means that ProcessPoolExecutor failed due to "too many files open".  

![comparison image didn't show](./images/comparison_2.png)  

## Installation

`python3 -m pip install fast_map`


## Troubleshooting and issues 
Accessing thread-safe objects (created externally, and using locks under the hood) within the function supplied to fast\_map will probably result in a deadlock.

By default the fast\_map `threads_limit` parameter is `None`, meaning that a separate thread is spawned for **each** of supplied tasks (attempting to provide full concurrency). It is strongly encouraged to set threads\_limit to some reasonable value for 2 reasons:  
* large number of threads will slow down the CPU-expensive part of the blocking function  
* fast\_map will result in unhandled exception when too many threads try to be created   

(btw if threads\_limit is higher than the number of supplied tasks, then the number of created threads equals the number of supplied tasks, so threads\_limit doesn't force the number of created threads, it only limits them)  

## Implementation details
fast\_map uses multiprocessing module and its default process start method (which I believe is `fork` on Unix). It spawns the number of processes equal to the number of CPU cores. For each spawned process it uses a separate task supplying `multiprocessing.Queue` (each has its own for the sake of even task distribution). It uses a singl common results queue for collecting results. It uses `concurrent.futures.ThreadPoolExecutor` to implement multi-threading. It uses a single `threading.Thread` to enqueue all the tasks (this allows to start computation on multiple processes without the need to enqueue all the tasks first).   

It was inspired by a similar project which combined multiprocessing with asyncio:  
[asyncioeval](https://github.com/nbasker/tools/tree/master/asyncioeval) by Nicholas Basker


## Considerations
#### Why not use threading or multiprocessing on their own?  
Multithreading in Python uses a single core on multi-core processors. Multiprocessing isn't well suited to provide concurrency for large number of tasks (on my laptop it fails at around 1000 forked processes). Both of these combined appear to work well with functions expensive in terms or CPU work (e.g. `for i in range(10**6)`) and IO waiting time (e.g. `time.sleep(1)`).  

#### Why not use asyncio for concurrency instead of threading?  
I think asyncio is a good choice over multi-threading when we can modify a blocking function into an awaitable coroutine. If we want/must use a blocking function (e.g. we can't modify it into asyncio coroutine because it's from some library we can't modify) and we want to make it concurrent, asyncio provides `loop.run_in_executor` which relies on multi-threading anyway.   



