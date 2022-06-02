from loan.loan import FixedRateLoan, VariableRateLoan
from asset.asset_houses import HouseBase
import logging
from utils.memoize import Memoize


class MortgageMixin(object):
    def __init__(self, start, maturity, rate, face, home):
        if isinstance(home, HouseBase):
            super(MortgageMixin, self).__init__(start, maturity, rate, face, home)
        else:
            # log an error prior to raising the exception.
            logging.error('Home attribute needs to be a HomeBase type.')
            raise TypeError('Home attribute needs to be a HomeBase type.')

    def PMI(self, T):
        if T > self.term or T <= 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            logging.info('Entered T is greater than term')
            return 0  # if T entered is larger than the term or <= 0, return 0
        # if LTV is larger than 80%, the borrower has to pay the PMI
        LTV = self.balance(T) / self._asset.initialValue
        logging.debug(f'calculating the LTV at {T}: {LTV} = {self.balance(T)} (balance) / {self._asset.initialValue} '
                      f'(asset initial value)')
        if LTV > 0.8:
            logging.debug(f'{LTV} is larger than 0.8, so PMI is incurred at T = {T}')
            m_PMI = 0.000075 * self._face
            logging.debug(f'calculating PMI at {T}: {m_PMI} = {self._face} * 000075')
            return m_PMI
        else:  # else no PMI would be incurred
            logging.debug(f'{LTV} is less than 0.8, so PMI = 0 at T = {T}')
            return 0

    # The monthly payment is the payment of the loan + the PMI, depending on the period
    def monthlyPayment(self, T):
        return super(MortgageMixin, self).monthlyPayment(T) + self.PMI(T)

    # for outstanding balance we call the loan class
    # this is important to calculate the PMI
    def balance(self, T):
        return super(MortgageMixin, self).balance(T)

    # for interest due we simply call the one from Loan class
    def interestDue(self, T):
        return super(MortgageMixin, self).interestDue(T)

    def interestDueRecursive(self, T):
        if T > self.term or T < 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            logging.info('Entered T is greater than term')
            return 0  # if T entered is larger than the term of loan, return 0
        else:
            logging.warning('Recursive functions might take a long time, explicit versions are recommended')
            return self.interestDueRecursiveOutput(T)

    # the output function is for calculations inside the class, the user will not use this
    # will be called by the interestDueRecursive() to return the calculations
    def interestDueRecursiveOutput(self, T):
        return super(MortgageMixin, self).interestDueRecursiveOutput(T)

    # The principle due will use the monthly payment uniquely in this class to
    # minus the interest due
    def principalDue(self, T):
        return super(MortgageMixin, self).monthlyPayment(T) - self.interestDue(T)

    def principalDueRecursive(self, T):
        if T > self.term or T < 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            logging.info('Entered T is greater than term')
            return 0  # if T entered is larger than the term of loan, return 0
        else:
            logging.warning('Recursive functions might take a long time, explicit versions are recommended')
            return self.principalDueRecursiveOutput(T)

    # the output function is for calculations inside the class, the user will not use this
    # will be called by the principalDueRecursive() to return the calculations
    @Memoize
    def principalDueRecursiveOutput(self, T):
        return super(MortgageMixin, self).monthlyPayment(T) - self.interestDueRecursiveOutput(T)

    # the output function is for calculations inside the class, the user will not use this
    # will be called by the balanceRecursive() to return the calculations
    @Memoize
    def balanceRecursiveOutput(self, T):
        if T == 0:
            return self._face
        else:
            return self.balanceRecursiveOutput(T - 1) - self.principalDueRecursiveOutput(T)

    def balanceRecursive(self, T):
        if T > self.term or T < 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            logging.info('Entered T is greater than term')
            return 0  # if T entered is larger than the term of loan, return 0
        else:
            logging.warning('Recursive functions might take a long time, explicit versions are recommended')
            return self.balanceRecursiveOutput(T)

    # for total payments we simply call the one from Loan class
    def totalPayments(self):
        return sum(self.monthlyPayment(t) for t in range(self.term))


# The variable mortgage class, derived from both mortgageMixin
# and the VariableRateLoan class
class VariableMortgage(MortgageMixin, VariableRateLoan):
    pass


# The fixed mortgage class, derived from both mortgageMixin
# and the FixedRateLoan class
class FixedMortgage(MortgageMixin, FixedRateLoan):
    pass
