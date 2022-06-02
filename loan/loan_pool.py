from loan.loan_base import Loan
from loan.auto_loan import AutoLoan
from loan.mortgage import FixedMortgage
from asset.asset_cars import Car, Civic, Lexus, Lambourghini
from asset.asset_houses import VacationHome, PrimaryHome
from functools import reduce
import logging
import random
import numpy as np

# these dicts are to read the csv and create the loans in class
loanNameToClass = {
    'Auto Loan': AutoLoan,
    'Fixed Mortgage': FixedMortgage
}

assetNameToClass = {
    'Lambourghini': Lambourghini,
    'Car': Car,
    'Lexus': Lexus,
    'Civic': Civic,
    'VacationHome': VacationHome,
    'PrimaryHome': PrimaryHome,
}


class LoanPool(object):
    # the loans will be in list, because a pool usually contains multiple loans
    def __init__(self, loans):
        self._loans = loans

    # This is to make LoanPool class to be an iterable
    # be able to loop over a LoanPool object’s individual Loan objects
    def __iter__(self):
        for loan in self._loans:
            yield loan  # generator

    # This is a class method that would write to the csv
    @classmethod
    def writeLoansToCSV(cls, loanPool, filename):
        lines = []

        for loan in loanPool:
            lines.append(','.join([loan.__class__.__name__, loan.asset.__class__.__name__,
                                   str(loan.asset.initialValue), str(loan.face),
                                   str(loan.rate), str(loan.start), str(loan.maturity)]))

        outputString = '\n'.join(lines)

        with open(filename, 'w') as fp:
            fp.write(outputString)

    # This is a class method that would create the loan
    @classmethod
    def createLoan(cls, loanType, principal, rate, term, assetName, assetValue):
        assetCls = assetNameToClass.get(assetName)
        if assetCls:
            asset = assetCls(float(assetValue))
            loanCls = loanNameToClass.get(loanType)
            if loanCls:
                loan = loanCls(int(term), float(rate), float(principal), asset)
                return loan
        else:
            logging.error('Invalid loan type entered.')

    # returns the number of ‘active’ loans. Active loans are loans that have a
    # balance greater than zero.
    def activeLoanCount(self, T):
        # use list comprehension to create a list for loans that have balance > 0
        active_list = [loan for loan in self._loans if loan.balance(T) > 0]
        return len(active_list)  # return the length of the active loan list

    # This function determines that it is in default if it gets a 0
    # logic of this checkDefaults: the default probability = the probability that 0 will be selected
    def checkDefaults(self, T):
        required_key = max(period for period in Loan.default_dict.keys() if period <= T)  # using generator expression
        default_prob = Loan.default_dict[required_key]  # retrieve the prob from the dict
        random_range = round(1 / default_prob) - 1  # random range should be reduced by one to include 0
        recovery_value = 0
        for loan in self._loans:
            if not loan.default_status:  # check only when defaulted flag is false
                loan.checkDefault(random.randint(0, random_range))  # update the loan default status
                if loan.default_status:  # if loan is default, return the recovery value of the asset
                    recovery_value += loan.recoveryValue(T)
        return recovery_value  # return all the defaulted loan's asset recovery value

    # This is to calculate Weighted Average Rate (WAR) of the loans
    def WAR(self, T):
        # use the reduce function with callable lambda to calculate the sum
        # numerator: sum of each loan with the rate * face
        # denominator: sum of the face value of each loan
        logging.debug('calculating the WAR...')
        wr_sum = reduce(lambda total, loan: total + (loan.face * loan.getRate(T)), self._loans, 0) / \
                 reduce(lambda total, loan: total + loan.face, self._loans, 0)
        war = round(wr_sum * 100, 2)  # round the weighted average rate to the nearest hundredths.
        return str(war) + ' %'

    # This is to calculate the Weighted Average Maturity (WAM)
    def WAM(self):
        # use the reduce function with callable lambda to calculate the sum
        # numerator: sum of each loan with the rate * term in months/12
        # denominator: sum of the face value of each loan
        logging.debug('calculating the WAM...')
        wam_sum = reduce(lambda total, loan: total + (loan.face * loan.term / 12), self._loans, 0) / \
                  reduce(lambda total, loan: total + loan.face, self._loans, 0)
        return round(wam_sum, 3)

    # sum up all the face/principal amount of the loans in the pool
    # using list comprehension
    def totalPrincipal(self):
        total_principal = sum(loan.face for loan in self._loans)
        # logging.debug('calculating the total principal = sum of each face value in the pool')
        return total_principal

    # sum up all the payment amounts of the loans in the pool
    # using generator expression
    def totalPayments(self):
        return sum(loan.totalPayments() for loan in self._loans)

    # for total interest, instead of calling the function for each loan
    # I decide to simply use total payments - total principal in the pool
    def totalInterest(self):
        return self.totalPayments() - self.totalPrincipal()

    # find the principal due at given period T
    # using generator expression
    def principalDue(self, T):
        return sum(loan.principalDue(T) for loan in self._loans)

    # find the total payment due at given period T
    # using generator expression
    def paymentDue(self, T):
        return sum(loan.monthlyPayment(T) for loan in self._loans)

    # find the interest due at given period T
    # using generator expression
    def interestDue(self, T):
        return sum(loan.interestDue(T) for loan in self._loans)

    # find the balance outstanding at given period T
    # using generator expression
    def balance(self, T):
        return sum(loan.balance(T) for loan in self._loans)

    # This function will return a list of lists of the data in each loan
    def getWaterfall(self, T):
        res_lst = []
        for loan in self._loans:
            res_lst.append([loan.balance(T), loan.monthlyPayment(T), loan.principalDue(T), loan.interestDue(T)])
        return res_lst

    def reset(self):
        for loan in self._loans:
            loan.reset()
