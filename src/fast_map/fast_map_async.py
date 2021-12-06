from fast_map import fast_map
from threading import Thread, Lock

def fast_map_async(*args, **kwargs):
    ''' Returns a reference to the spawned thread.
        User may supply the following callbacks:
        - on_result   (having a single argument - result)
        - on_done     (no arguments)

        Usage:

        import time
        def task(x):
            time.sleep(1)
            return x*x

        def on_result(result):
            print(result)

        def on_done():
            print('all done')

        t = fast_map_async(
                task,
                range(8), # argument list to tasks
                on_result = on_result,
                on_done = on_done,
                threads_limit = 100
                )

        # returned thread may be used to "t.join()" if we want
    '''

    def thread(args, kwargs):
        on_result = kwargs.pop('on_result', (lambda x:None))
        assert callable(on_result), 'supplied on_result is not callable'
        on_done = kwargs.pop('on_done', (lambda:None))
        assert callable(on_done), f'supplied on_done is not callable'
        for result in fast_map(*args, **kwargs):
            on_result(result)
        on_done()

    t = Thread(target=thread, args=[args, kwargs])
    t.start()
    return t

if __name__ == '__main__':
    pass
