from loan.loan_base import Loan
import logging


# This loan has the same interest rate throughout
class FixedRateLoan(Loan):
    pass


# This loan has a different rate depending on the period
class VariableRateLoan(Loan):
    def __init__(self, term, rateDict, face, asset):
        # make sure the rate is entered as dictionary
        if type(rateDict) is not dict:
            logging.error('Entered rate needs to be a dict!')
            raise TypeError('Entered rate needs to be a dict!')
        else:
            super(VariableRateLoan, self).__init__(term, rateDict, face, asset)
            self._rateDict = rateDict

    # overrides the base class
    def getRate(self, T):
        # if the period entered is larger than the term of the loan, or invalid T(<0)
        # simply return 0
        if T > self.term() or T < 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            logging.info('Entered T is greater than term')
            return 0
        # this is to infer the rate at the term entered
        # we would always want the largest term equal to or below T
        required_key = max(term for term in self._rateDict.keys() if term <= T)  # using generator expression
        return self._rateDict[required_key]  # return the rate by using key to retrieve the val in dict
