import itertools
from asset.asset_cars import Car
from loan.mortgage import FixedMortgage
from loan.auto_loan import AutoLoan
from liabilities.structured_securities import StructuredSecurities
from loan.loan_pool import LoanPool
from utils.waterfall import doWaterfall
import logging
import csv

# set the level to WARNING level
logging.getLogger().setLevel(logging.WARNING)

'''
PART One: In this program, load the csv data into the LoanPool class and calculate the waterfall
The waterfall tracks all the cashflows through each time period.
The pool of loans (the assets) will provide a monthly cashflow (resulting from the individual loan
monthly payments) and that cashflow is allocated to each of the tranches in the structure (the liabilities).
'''
'''
Part Two:
In this program, test the waterfall Metrics: IRR, DIRR, AL, and Letter Rating
All these metrics are important for investors to analyze the tranches
'''

'''
One thing to notice for testing purpose: in order to speed up the run time of doWaterfall,
I intentionally commented out most of the logging.debug inside loan class (speed up from 5 secs to 1.4 secs now)
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
    # since I put the csv file inside this project, I don't have to specify C:\\
    with open('Loan Test\\Loans.csv', 'r') as fp:
        reader = csv.reader(fp)  # use the csv reader for simplicity
        header = next(reader)  # we don't want to load the header
        for row in reader:  # read each row, so the index will be column of each row
            res_lst.append(loanNameToClass[row[1]](float(row[4]), float(row[3]), float(row[2]),
                                                   assetNameToClass[row[5]](float(row[6]))))

    # # another method to load the data by using the function inside the loan_pool class
    # with open('C:\\Loan Test\\Loans.csv', 'r') as fp:
    #     reader = csv.reader(fp)  # use the csv reader for simplicity
    #     header = next(reader)  # we don't want to load the header
    #     for row in reader:  # read each row, so the index will be column of each row
    #         res_lst.append(LoanPool.createLoan(row[1], row[2], row[3], row[4], row[5], row[6]))

    # now create the LoanPool object with the res_lst
    pool1 = LoanPool(res_lst)

    # instantiate the structured securities
    securities1 = StructuredSecurities(pool1.totalPrincipal())
    # now add two standard tranches
    securities1.addTranche(0.8, 0.02, 0)  # subordination is used to sort the two tranches, 0 goes before 1
    securities1.addTranche(0.2, 0.06, 1)
    securities1.mode = 'Sequential'  # set the mode to Sequential or Pro Rata

    LoanPoolWaterfall, StructuredSecuritiesWaterfall, ReserveAccount, ratingMetrics = doWaterfall(pool1, securities1)
    # time taken for a single doWaterfall() is: 1.39s
    # I got rid of the debug in order to reduce the time taken

    # ******** Below are the codes to create the CSV files from Part one ********
    with open('C:\\Loan Test\\Loan Pool Waterfall.csv', 'w') as fp:
        # this is the path of creating a new file
        header_list = []
        # add header line for each loan
        for i in range(len(LoanPoolWaterfall[0])):
            header = ['Loan ' + str(i + 1) + ' Outstanding Balance', 'Loan ' + str(i + 1) + ' Monthly Payment',
                      'Loan ' + str(i + 1) + ' Principal Due', 'Loan ' + str(i + 1) + ' Interest Due']
            header_list.append(header)
        flattened_headers = [item for sublist in header_list for item in sublist]
        fp.write(','.join(map(str, list(flattened_headers))) + '\n')

        # do loan waterfall and save results in one csv file
        for loans in LoanPoolWaterfall:
            # we need to dig out the items in the sublist of the list
            full_loan_lst = [item for sublist in loans for item in sublist]
            fp.write(','.join(map(str, list(itertools.chain(full_loan_lst)))) + '\n')

    with open('C:\\Loan Test\\Structured Securities Waterfall.csv', 'w') as fp:
        header_list = []
        # add header line for each loan
        for i in range(len(StructuredSecuritiesWaterfall[0])):
            header = ['Tranche ' + str(i + 1) + ' Notional Balance', 'Tranche ' + str(i + 1) + ' Interest Due',
                      'Tranche ' + str(i + 1) + ' Current Interest Paid', 'Tranche ' + str(i + 1) +
                      ' Interest Shortfall', 'Tranche ' + str(i + 1) + ' Current Principal Paid']
            header_list.append(header)
        header_list.append(['Reserve Account'])
        flattened_headers = [item for sublist in header_list for item in sublist]
        fp.write(','.join(map(str, list(flattened_headers))) + '\n')

        # do loan waterfall and save results in one csv file
        for tranche, reserve in zip(StructuredSecuritiesWaterfall, ReserveAccount):
            # we need to dig out the items in the sublist of the list
            full_tranche_lst = [item for sublist in tranche for item in sublist]
            fp.write(','.join(map(str, list(itertools.chain(full_tranche_lst)) + [str(reserve)])) + '\n')
        # Each tranche's balance gets successfully paid down to 0.
        # There are money left in the reserve account at the end

    # ******** This is the newly added part for PART2 Waterfall Metrics ********
    # display the metrics to the screen
    print('{0:<10s} {1:<10s} {2:<10s} {3:<10s}'.format('IRR', 'DIRR', 'AL', 'Rating'))
    for tranche_metric in ratingMetrics:
        print(f'{tranche_metric[0]:<10f}{tranche_metric[1]:<10f}{tranche_metric[2]:<10f}{tranche_metric[3]:<10s}')


if __name__ == '__main__':
    main()
