from time import time
from tdc_python_utils.colours import highlight_text

def execution_time(func):
    def timer(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)  # capture the function's output
        d = round(time() - t1, 2)
        print(highlight_text(f"Execution time: {d} seconds", d, color="cyan"))
        return result  # return it so the caller gets the dataframe
    return timer
