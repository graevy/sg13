from timeit import timeit


# you'll want to read the timeit.timeit documentation before reading this file

# this has become more useful than timeBatch
# still best to use timeBatch for bulk comparisons
def timed(func):
    """decorator wrapper for timing function runtime in-file.
    RESERVED KWARGS:
    loops (int, for timeit loops), 
    digits (int, for rounding), 
    skipIO (bool, to skip terminal IO), 
    verification, and verificationData (bool and any, to check output against)

    Args:
        func (function): to time
    """
    def inner(*args, loops=100000, digits=5, skipIO=False, verification=False, verificationData=None, **kwargs):
        # see timeitNamespace explanation at end of file
        timeitNamespace = {}
        timeitNamespace[func.__name__] = func
        timeitNamespace['args'] = args
        timeitNamespace['kwargs'] = kwargs
        # timeit basically does exec(timeitStatement)
        timeitStatement = func.__name__+"(*args, **kwargs)"

        # begin printing
        if not skipIO:
            # run function once for output
            output = func(*args, **kwargs)

            # checking correctness. i opted for 2 vars incase output is None, False, etc
            if verification:
                if output == verificationData:
                    print(f"Function {func.__name__}: SUCCESS")
                else:
                    print(f"Function {func.__name__}: FAILURE. "+\
                          f"Expected type {type(verificationData)}: {repr(verificationData)}")
            else:
                print(f"Function {func.__name__}:")

            # sometimes the output is too verbose for my terminal, so i cut it off here
            paramStr = repr(list(args) + list(kwargs.items()))
            if len(paramStr) > 50:
                print(f"    Input:     {paramStr[:50]} ...")
            else:
                print(f"    Input:     {paramStr}")

            output = repr(output)
            if len(output) > 50:
                print(f"    Output:    {output[:50]} ...")
            else:
                print(f"    Output:    {output}")

            # print the (rounded) time
            suffix = 's' if loops != 1 else ''

            duration = round(timeit(timeitStatement, globals=timeitNamespace, number=loops), digits)
            print(f"    Execution time over {loops} iteration{suffix}: {duration}s")
        return duration
    return inner


# TODO: support for functions with more than 1 param, or class obj params
# (add class obj params to timeitNamespace)
def timeBatch(data, *funcs, loops=100000, digits=5, skipIO=False, verification=False, verificationData=None):
    """prints function(s) output and runtime over datapoints 

    Args:
        data (iterable): a container of data
        *funcs (function): functions to evaluate
        loops (int, optional): number of iterations (for runtime calc)
                           per datapoint per function. Defaults to 100000.
        digits (int, optional): number of digits to round output with. Defaults to 5.
        skipIO (bool, optional): skip printing output? Defaults to False.
        verification (bool, optional): check output correctness? Defaults to false.
        verificationData (type(data), optional): data for verification. Defaults to None.
    """
    # see timeitNamespace explanation at end of file
    timeitNamespace = {}
    for func in funcs:
        timeitNamespace[func.__name__] = func

    results = []
    # i categorize the results by datapoint instead of by function for readability, mostly
    for point in data:
        pointResults = []

        for func in funcs:
            # timeit basically runs exec(timeitStatement)
            timeitStatement = f"{func.__name__}({repr(point)})"
            # this is where the calculation actually happens
            duration = timeit(timeitStatement, number=loops, globals=timeitNamespace)
            duration = round(duration, digits)
            # to get the function output i have to just run it again
            # not ideal for slow functions.
            # TODO: a decorator that saves output to pass to timing functions?
            output = func(point)
            if verification:
                if output == verificationData:
                    pointResults.append((duration, func.__name__, output, True))
                else:
                    pointResults.append((duration, func.__name__, output, False))
            else:
                pointResults.append((duration, func.__name__, output))

        pointResults.sort()
        results.append((point,pointResults))

        # printing the output
        if not skipIO:
            suffix = 's' if loops != 1 else ''
            if verification:
                print(f"Runtimes for datapoint {point} over {loops} iteration{suffix}:")
                # the key function here sorts by the last element (correctness) instead of the first (duration)
                for duration, funcName, output, correctness in sorted(pointResults, key=lambda x: x[-1], reverse=True):
                    if correctness:
                        print(f"    {funcName} successfully yielded {output} in {duration} seconds")
                    else:
                        print(f"    {funcName} failed to yield {output} in {duration} seconds")
            else:
                print(f"Runtimes for datapoint {point} over {loops} iteration{suffix}:")
                for duration, funcName, output in pointResults:
                    print(f"    {funcName} yielded {output} in {duration} seconds")

    return results


# timeit operates in its own namespace. this is a huge
# (but necessary) headache to achieve greater timing accuracy.
# but you can import another namespace with its globals() param.
# this requires all calling functions to import their globals() as an arg.
# i've circumvented this by making a dict to pass as a namespace to timeit.
# it's maybe easier to conceptualize this as timeit's __init__ method

# a previous version used timeit's setup param to import calling modules
# into timeit's namespace by examining the stack.
# that ended up being really slow, and it required calling modules
# to hide code behind "if __name__ == '__main__'" statements anyway.
# i think, ideally, timeit could just pull vars from memory with
# memoryview() or some ctypes pointer tricks
