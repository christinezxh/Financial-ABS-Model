"""
This is the derived class from Tranche
Standard tranches receive both interest and principal payments from the pool of loans
"""

from liabilities.tranche_base import Tranche
import logging


class StandardTranche(Tranche):
    def __init__(self, face, rate, face_percent, subordination):
        super(StandardTranche, self).__init__(face, rate, face_percent, subordination)
        self._currentPeriod = 0  # initialize current time period to 0
        self._currentPrincipalDue = 0  # initialize the principal due to 0
        self._principalShortfall = 0  # initialize the principal shortfall to 0
        self._currentPrincipalPaid = 0  # initialize current principal paid to 0
        self._currentInterestDue = 0  # initialize the interest due to 0
        self._currentInterestPaid = 0  # initialize current interest paid to 0
        self._interestShortfall = 0  # initialize a special case of current interest due to 0
        self._currentNotionalBalance = self.face  # initialize the balance to face value

    # This static-level method will return the monthly interest rate for a passed-in annual rate
    @staticmethod
    def monthlyRate(annualRate):
        return annualRate / 12

    # This func would increase the current time period by 1
    def increaseTimePeriod(self):
        self._currentPeriod += 1
        # when increase the time period, we should reset all current payment to 0 the current interest due = balance
        # of the previous period times the monthly rate (remember it's monthly not annual) the interest shortfall
        # will be added to the interest owed
        self._currentInterestDue = self._currentNotionalBalance * self.monthlyRate(self.rate) + self._interestShortfall
        self._currentPrincipalPaid = 0  # reset current principal paid to 0
        self._currentInterestPaid = 0  # reset current interest paid to 0
        self._interestShortfall = 0  # reset current interest short fall after adding it to interest due

    # This func would record a principal payment for the current object time period
    def makePrincipalPayment(self, PMT, dueAmount):  # PMT would be the cash payment made by user
        # dueAmount is the PrincipalDue that will be passed by the loan class later in doWaterfall
        # to make sure that only be allowed to be called once for a given time period
        if self._currentPrincipalPaid > 0:  # this means principal already been paid
            logging.info('Principal Payment already been made for this time period')
        elif self._currentNotionalBalance == 0:  # this means balance is already 0
            logging.info('Balance is already 0, payment is not accepted any more')
        else:
            # use min to make sure we are not accepting anything more than current balance
            # it's the lesser of the balance or the principal due + previous shortfall during the period
            self._currentPrincipalDue = min(self._currentNotionalBalance, dueAmount + self._principalShortfall)
            self._currentPrincipalPaid = min(self._currentPrincipalDue, PMT)
            # reduce the outstanding notional balance by the payment made
            # if the payment made is less than the current balance
            self._currentNotionalBalance -= self._currentPrincipalPaid
            # self.notionalBalance = self._currentNotionalBalance - self._currentPrincipalPaid
            # no need to reset it back to 0 manually because it will be recalculated for every new payment
            self._principalShortfall = self._currentPrincipalDue - self._currentPrincipalPaid
            # reduce the current outstanding balance after making the payment
        return PMT - self._currentPrincipalPaid  # if customer paid more than the balanced owed, return the portion

    # This func would record an interest payment for the current object time period
    def makeInterestPayment(self, PMT):
        # to make sure that only be allowed to be called once for a given time period
        if self._currentInterestPaid > 0:  # this means principal already been paid
            logging.info('Interest Payment already been made for this time period')
        elif self._currentInterestDue == 0:  # this means interest due in this period is already 0
            logging.info('There is no current interest due, payment is not accepted any more')
        else:
            # use min to make sure we are not accepting anything more than current balance
            self._currentInterestPaid = min(self._currentInterestDue, PMT)
            # if the payment is less than the current interest due, shortfall would be incurred
            self._interestShortfall = self._currentInterestDue - self._currentInterestPaid
            # remember to add the interest shortfalls to the balance due
        return PMT - self._currentInterestPaid  # if customer paid more than the balanced owed, return the portion

    # This would reset the tranche to its original state, time=0
    def reset(self):
        self._currentPeriod = 0  # reset current time period to 0
        self._currentPrincipalPaid = 0  # reset current principal paid to 0
        self._currentInterestPaid = 0  # reset current interest paid to 0
        self._interestShortfall = 0  # reset a special case of current interest due to 0
        self._currentNotionalBalance = self.face  # reset balance back to face
        self._currentInterestDue = 0  # reset current interest due to 0

    # setters and getters for some member data
    @property
    def currentPeriod(self):
        return self._currentPeriod

    @currentPeriod.setter
    def currentPeriod(self, icurrentPeriod):
        self._currentPeriod = icurrentPeriod

    @property
    def currentPrincipalDue(self):
        return self._currentPrincipalDue

    @currentPrincipalDue.setter
    def currentPrincipalDue(self, icurrentPrincipalDue):
        self._currentPrincipalDue = icurrentPrincipalDue

    @property
    def interestDue(self):
        return self._currentInterestDue

    @property
    def notionalBalance(self):
        return self._currentNotionalBalance
        # return self.face - self._sumPrincipalPaid

    @property
    def currentInterestPaid(self):
        return self._currentInterestPaid

    @property
    def currentPrincipalPaid(self):
        return self._currentPrincipalPaid

    @property
    def interestShortfall(self):
        return self._interestShortfall
