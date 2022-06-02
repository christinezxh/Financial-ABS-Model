from functools import wraps


# a decorator that memoize’s the result of a function
def Memoize(function):
    cache = {}  # create an empty dict that will store the value of functions with intense calculations

    @wraps(function)  # ensure the correct output
    def wrapped(*args, **kwargs):
        if (str(args), str(kwargs)) not in cache:
            # call func() and store the result
            cache[(str(args), str(kwargs))] = function(*args, **kwargs)
        return cache[(str(args), str(kwargs))]

    return wrapped
