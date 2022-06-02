from simulations.simulate_waterfall import simulateWaterfall
from simulations.simulation_parallel import runSimulationParallel
from liabilities.tranche_base import Tranche

'''
For flexibility, I think pass in the tranche percent and rates as two arguments for the function
might be better. 
'''


def runMonte(loanpool, structured_securities, tolerance, NSIM):
    # Because we are given the predetermined rates, so initialize inside the functions
    tranche_percent = [0.8, 0.2]
    coeff = [1.2, 0.8]  # Tranche A has coeff of 1.2, Tranche B has coeff of 0.8
    rates = [0.05, 0.08]  # Tranche A has rate of 5%, Tranche B has rate of 8%
    structured_securities.addTranche(tranche_percent[0], rates[0], 0)
    structured_securities.addTranche(tranche_percent[1], rates[1], 1)
    while True:
        new_rates = []  # reset the new_rates every time
        yields = []  # Tranche A has rate of 5%, Tranche B has rate of 8%
        for index, tranche in enumerate(structured_securities.trancheList):
            tranche.rate = rates[index]  # give each tranche a new rate based on the original or modified rate
        average_DIRR_AL = simulateWaterfall(loanpool, structured_securities, NSIM)
        yields.append(Tranche.calculateYield(average_DIRR_AL[0][0], average_DIRR_AL[0][1]))
        yields.append(Tranche.calculateYield(average_DIRR_AL[1][0], average_DIRR_AL[1][1]))
        for index, tranches in enumerate(structured_securities.trancheList):
            new_rates.append(Tranche.newTrancheRate(tranches.rate, coeff[index], yields[index]))
        diffs = Tranche.diff(tranche_percent, rates, new_rates)
        if diffs < tolerance:
            break
        rates = new_rates  # modify the tranche rate to reflect the yields, return to the while loop

    for index, tranche in enumerate(structured_securities.trancheList):
        # now append the rating and the rate of each tranche to the result list
        average_DIRR_AL[index].append(Tranche.DIRR_Rating(average_DIRR_AL[index][0]))
        average_DIRR_AL[index].append(tranche.rate)

    return average_DIRR_AL  # output the DIRR, Rating, WAL, and rate of each tranche


# The only modification here with runMonteParallel is using the runSimulationParallel() instead of
# the simulateWaterfall to get the average_DIRR_AL

def runMonteParallel(loanpool, structured_securities, tolerance, NSIM, numProcesses):
    # Because we are given the predetermined rates, so initialize inside the functions
    tranche_percent = [0.8, 0.2]  # initialize Tranche A to take 80%, could be changed later
    coeff = [1.2, 0.8]  # Tranche A has coeff of 1.2, Tranche B has coeff of 0.8
    rates = [0.05, 0.08]  # Tranche A has rate of 5%, Tranche B has rate of 8%
    structured_securities.addTranche(tranche_percent[0], rates[0], 0)
    structured_securities.addTranche(tranche_percent[1], rates[1], 1)
    while True:
        new_rates = []  # reset the new_rates every time
        yields = []  # initialize the yields, reset yields every time
        for index, tranche in enumerate(structured_securities.trancheList):
            tranche.rate = rates[index]  # give each tranche a new rate based on the original or modified rate
        # because the tranches are already sorted, so we don't have to worry about the order
        average_DIRR_AL = runSimulationParallel(loanpool, structured_securities, NSIM, numProcesses)
        yields.append(Tranche.calculateYield(average_DIRR_AL[0][0], average_DIRR_AL[0][1]))
        yields.append(Tranche.calculateYield(average_DIRR_AL[1][0], average_DIRR_AL[1][1]))
        for index, tranches in enumerate(structured_securities.trancheList):
            # call the class method of newTrancheRate to get the new rates based on current rate, coeff and yields
            new_rates.append(Tranche.newTrancheRate(tranches.rate, coeff[index], yields[index]))
        diffs = Tranche.diff(tranche_percent, rates, new_rates)
        if diffs < tolerance:
            break  # if diff calculated is smaller than tolerance, break the loop
        rates = new_rates  # modify the tranche rate to reflect the yields, return to the while loop

    for index, tranche in enumerate(structured_securities.trancheList):
        # now append the rating and the rate of each tranche to the result list
        average_DIRR_AL[index].append(Tranche.DIRR_Rating(average_DIRR_AL[index][0]))
        average_DIRR_AL[index].append(tranche.rate)

    return average_DIRR_AL  # output the DIRR, Rating, WAL, and rate of each tranche
