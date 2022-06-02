from utils.timer import Timer
from asset.asset_cars import Car
from loan.mortgage import FixedMortgage
from loan.auto_loan import AutoLoan
from liabilities.structured_securities import StructuredSecurities
from loan.loan_pool import LoanPool
from simulations.monte import runMonte, runMonteParallel
import logging
import csv

# remember to set the level to WARNING level
logging.getLogger().setLevel(logging.WARNING)

'''
In this program, I utilize multiprocessing to speed up the runMonte 
with a new function called runMonteParallel (I decided to create a new one and kept runMonte); 
functionality of runMonteParallel is the same as runMonte, 
the only difference is that I implemented multiprocessing
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
    securities2 = StructuredSecurities(pool1.totalPrincipal())
    # now add two standard tranches
    securities2.mode = 'Sequential'  # set the mode to sequential
    # because we predefine the rate of the two tranches to be 0.05 and 0.08 respectively
    # we don't have to add any branches here again

    # ******** using runMonteParallel with multiprocessing ********
    # we could see a big improvement in time taken
    with Timer('runMonteParallel Minutes Timer') as timer:
        res_Parallel = runMonteParallel(pool1, securities2, 0.005, 100, 20)
        timer.configureTimerDisplay('min')

    # now print the results
    print(f'DIRR       AL      Letter Rating    Rates')
    for tranche in res_Parallel:
        print(f'{tranche[0]:<11f}{tranche[1]:<11f}{tranche[2]:<11s}{tranche[3]:<11f}')
    # NSIM = 2000, num of processes = 20, time taken: 21 minutes, much faster!!!
    # NSIM = 2000, num of processes = 25, time taken is: 19.92 minutes
    # NSIM = 2000, num of processes = 40, time taken is: 10.87 minutes
    # NSIM = 2000, num of processes = 50, time taken is : 9 minutes
    # NSIM = 2000, num of processes = 200, time taken is : 4 minutes


if __name__ == '__main__':
    main()
