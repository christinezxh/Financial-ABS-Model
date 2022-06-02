from loan.loan_pool import LoanPool
from utils.waterfall import doWaterfall
from liabilities.structured_securities import StructuredSecurities
import math
import numpy as np
import logging


def simulateWaterfall(loanpool, structured_securities, NSIM):
    if not isinstance(loanpool, LoanPool) or not isinstance(structured_securities, StructuredSecurities):
        logging.error('Please enter the correct class type')
    rating_metrics = []  # intialize an empty list to get the doWaterfall results
    # create an array filled with zeros, could be used to filled in later
    sum_DIRR_AL = np.zeros((len(structured_securities.trancheList), 2))
    for i in range(NSIM):
        # remember to reset each time of the simulation
        loanpool.reset()
        structured_securities.reset()
        # obtain the results of rating metrics from the doWaterfall
        rating_metrics.append(doWaterfall(loanpool, structured_securities)[3])
    for simulations in rating_metrics:
        for i, tranche_metric in enumerate(simulations):
            if tranche_metric[2] != math.inf:  # if AL not infinite
                sum_DIRR_AL[i] += [tranche_metric[1], tranche_metric[2]]
            else:
                # if AL is infinite, get rid of the AL, only add up the DIRR to get the average
                sum_DIRR_AL[i] += [tranche_metric[1], 0]
    # return the average DIRR and AL values for each tranche
    # use ndarray here because it allows to divide directly instead of doing a list comprehension
    DIRR_AL = sum_DIRR_AL / NSIM
    DIRR_AL = DIRR_AL.tolist()  # convert the array to list
    return DIRR_AL
