import time
import logging  # use a logging statement (info level) instead of a print statement
from functools import wraps


# this Timer class will play the function of time
# it will record the time taken for code running time
class Timer(object):
    # a class-level variable, defaults to 1 minute (60 seconds)
    warnThreshold = 60

    def __init__(self, msg, configure=None):
        self._start = None  # initialize the start time to None because not yet started
        self._running = False  # initialize the running to False because not yet running
        self._end = None  # initialize the end time to None because not yet started
        self._result = None
        self._msg = msg
        # initialize the configuration to seconds (default) or the configure that user passed in
        self._configure = configure

    # Modify the Timer class to work as a context manager
    def __enter__(self):
        self.start()  # when entering, should call the start() to start the timer
        return self

    # exit and display the message by calling end()
    def __exit__(self, *args):
        # when exit, should call the end(), display the results and exit the timer
        self.end()

    # set the configure with this function by passing in the type
    # min for minutes, hrs for hours, any other letter or nothing would be set to seconds
    # so if the user does not specify a type, it will be default type of seconds
    def configureTimerDisplay(self, configureType):
        self._configure = configureType

    def start(self):
        if self._running:  # if the Timer is currently running, print out an error message
            logging.info(f'Timer is already started!')
        else:
            self._start = time.time()
            self._running = True  # we need to set the running to True once we started the Timer

    def end(self):
        if not self._running:  # if the Timer is not currently running, print out an error message
            logging.info(f'Timer is not currently running!')
        else:
            self._end = time.time()
            self._result = self._end - self._start
            # a dict that contains hours and minutes, so later could be used for division
            divDict = {'h': 3600, 'min': 60}
            # a simple if else statement for all the conditions
            # if the result is larger than the threshold, trigger warning, else trigger info
            logFunc = logging.info if self._result < self.warnThreshold else logging.warning
            # the _configure would be the key, to achieve value in the dict
            # for minutes, divided by 60, four hours divided by 3600, if not, just divided by 1
            logFunc(f'{self._msg}: {self._result / divDict.get(self._configure, 1)}')
            self._running = False  # we need to set the running to False once we ended the Timer
            self._start = None  # set start back to none after the current timer stops
            self._end = None  # set end back to none after the current timer stops

    # This function will retrieve the last result of the time taken
    def retrieveLastResult(self):
        # a dict that contains hours and minutes, so later could be used for division
        divDict = {'h': 3600, 'min': 60}
        # a simple if else statement for all the conditions
        # if the result is larger than the threshold, trigger warning, else trigger info
        logFunc = logging.info if self._result < self.warnThreshold else logging.warning
        # the _configure would be the key, to achieve value in the dict
        # for minutes, divided by 60, four hours divided by 3600, if not, just divided by 1
        logFunc(f'{self._msg}: {self._result / divDict.get(self._configure, 1)}')

    # This function is to reset the timer explicitly, I put it here just to create more flexibility
    def reset(self):
        if not self._running:
            self._start = None  # reset the start time to None because not yet started
            self._running = False  # reset the running to False because not yet running
            self._end = None  # reset the end time to None because not yet started


# This is a decorator function
def Timer_decorator(function):
    @wraps(function)  # ensure the correct output
    def wrapped(*args, **kwargs):  # this is an internal function
        s = time.time()  # start time
        result = function(*args, **kwargs)  # call the function in the external Timer()
        e = time.time()  # end time
        print(f'Function {function}: {e - s} seconds')  # print the result, time usage of the input function
        return result  # return the function result

    return wrapped  # return the internal wrapped()


