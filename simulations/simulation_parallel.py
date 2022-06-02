import numpy as np
from simulations.simulate_waterfall import simulateWaterfall
import multiprocessing


# doWork function can be any function with any argument
def doWork(input, output):
    while True:
        try:
            f, args = input.get(timeout=1)
            res = f(*args)
            output.put(res)
        except:
            output.put('Done')
            break


def runSimulationParallel(loan_pool, structured_securities, NSIM, numProcesses):
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()

    # add 20 runMC function items into input_queue
    for i in range(numProcesses):
        input_queue.put((simulateWaterfall, (loan_pool, structured_securities, int(NSIM / numProcesses))))
        # create 5 child processes

    processes = []  # initialize an empty list of process
    for i in range(numProcesses):
        p = multiprocessing.Process(target=doWork, args=(input_queue, output_queue))
        p.start()
        processes.append(p)  # append all the processes

    res = []  # result
    # return the result list
    while True:
        r = output_queue.get()
        if r != 'Done':
            res.append(r)
        else:
            break

    for p in processes:
        p.terminate()  # stop the process after done

    for p in processes:
        p.join()  # calling main processes to wait until all the processes are finished

    sum_DIRR_AL = np.zeros((len(structured_securities.trancheList), 2))
    # initialize a ndarray filled with zeros, so that I could change the value by specifying index
    for simulations in res:
        for i, tranche in enumerate(simulations):
            sum_DIRR_AL[i] += [tranche[0], tranche[1]]  # sum both DIRR and AL up

    DIRR_AL = sum_DIRR_AL / len(res)  # get the average by dividing the length of the outer list
    DIRR_AL = DIRR_AL.tolist()
    return DIRR_AL
