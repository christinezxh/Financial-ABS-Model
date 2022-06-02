from utils.timer import Timer
from asset.asset_cars import Car
from loan.mortgage import FixedMortgage
from loan.auto_loan import AutoLoan
from liabilities.structured_securities import StructuredSecurities
from loan.loan_pool import LoanPool
from simulations.simulate_waterfall import simulateWaterfall
from simulations.monte import runMonte
import logging
import csv

# remember to set the level to WARNING level
logging.getLogger().setLevel(logging.WARNING)

'''
In this program, the functionality of both simulateWaterfall and runMonte will be tested.
simulateWaterfall() with waterfall Metrics: IRR, DIRR, AL, and Letter Rating
All these metrics are important for investors to analyze the tranches
We first test the simulateWaterfall itself to get DIRR and AL
Then, test the runMonte to get DIRR, AL, Rating Letter, and rates of each tranche;
runMonte takes a relatively long time to run with a large NSIM, 
This will be optimized with the multiprocessing runMonteParallel in another Part3 test.py
'''


def main():
    res_lst = []
    # Two dicts in order to load the csv into class
    loanNameToClass = {
        'Auto Loan': AutoLoan,
        'Fixed Mortgage': FixedMortgage
    }
    assetNameToClass = {
        'Car': Car,
    }  # because we only have Car asset here, so only define this for simplicity

    # now read the csv in order to load the data into the class
    with open('C:\\Loan Test\\Loans.csv', 'r') as fp:
        reader = csv.reader(fp)  # use the csv reader for simplicity
        header = next(reader)  # we don't want to load the header
        for row in reader:  # read each row, so the index will be column of each row
            res_lst.append(loanNameToClass[row[1]](float(row[4]), float(row[3]), float(row[2]),
                                                   assetNameToClass[row[5]](float(row[6]))))
    # now create the LoanPool object with the res_lst
    pool1 = LoanPool(res_lst)

    # instantiate the structured securities
    securities1 = StructuredSecurities(pool1.totalPrincipal())
    # now add two standard tranches
    securities1.addTranche(0.8, 0.03, 0)  # subordination is used to sort the two tranches, 0 goes before 1
    securities1.addTranche(0.2, 0.07, 1)
    securities1.mode = 'Pro Rata'  # set the mode to Sequential or Pro Rata

    # ******** test simulateWaterfall  ********
    with Timer('simulateWaterfall Minutes Timer') as timer:
        res_lst = simulateWaterfall(pool1, securities1, 10)
        timer.configureTimerDisplay('min')
    print(f'DIRR       AL')
    for tranche in res_lst:
        print(f'{tranche[0]:<11f}{tranche[1]:<11f}')
    # time taken record:
    # NSIM = 10, time taken: 13.88 seconds
    # NSIM = 200, time taken: 4.86 minutes

    # ******** using runMonte without multiprocessing ********
    # instantiate the structured securities
    securities2 = StructuredSecurities(pool1.totalPrincipal())
    # now add two standard tranches
    securities2.mode = 'Sequential'  # set the mode to sequential
    # because we predefine the rate of the two tranches to be 0.05 and 0.08 respectively
    # we don't have to add any branches here again
    with Timer('runMonte Minutes Timer') as timer:
        res_Monte = runMonte(pool1, securities2, 0.005, 10)  # tolerance is 0.005
        timer.configureTimerDisplay('min')
        # now print the results
    print(f'DIRR       AL      Letter Rating    Rates')
    for tranche in res_Monte:
        print(f'{tranche[0]:<11f}{tranche[1]:<11f}{tranche[2]:<11s}{tranche[3]:<11f}')

    # time taken record:
    # NSIM = 10, time taken: 56.22s
    # NSIM = 200, time taken: 1129s or 18.82 minutes
    # NSIM = 2000, time taken: 280 minutes


if __name__ == '__main__':
    main()
