"""
StructuredSecurities class will be a composition of Tranche objects
Lists of tranche objects are included in StructuredSecurities
"""
import logging

from liabilities.tranche_base import Tranche
from liabilities.standard_tranche import StandardTranche


class StructuredSecurities(object):
    def __init__(self, total_face):
        self._total_face = total_face  # initialized with a total face amount
        self._trancheList = []  # initialize an internal list of tranches
        self._mode = 'Sequential'  # initialize the mode
        self._reserveAccount = 0  # initialize the reserve account (the extra cash goes into here)

    # This will add tranche to the tranche list
    def addTranche(self, face_percent, rate, subordination):
        # create a tranche with the passed-in param
        tranche = StandardTranche(face_percent * self._total_face, rate, face_percent, subordination)
        # now add this tranche to the tranche list
        self._trancheList.append(tranche)
        # always sort the tranche list after added a new tranche
        # use callable to pass in the key in order of subordination
        self._trancheList = sorted(self._trancheList, key=lambda tranche: tranche.subordination)

    # This func would increase the current time period by 1
    def increaseTimePeriod(self):
        for tranche in self._trancheList:  # call each tranche in the list
            tranche.increaseTimePeriod()  # increase the current time period for each tranche

    # This method would cycle through the tranches to make payments; interest, then principal
    # the different modes impact how the payment would be made
    def makePayments(self, cash_amount, dueAmount):
        # initialize cash_left = cash_amount
        cash_left = cash_amount + self._reserveAccount
        # any of the previous cash amount in reserve account will supplement the cash amount for the next period
        self._reserveAccount = 0  # reset the reserve account back to 0
        for tranche in self._trancheList:  # cycle through all interest payments, paying each tranche
            cash_left = tranche.makeInterestPayment(cash_left)
            # the makeInterestPayment func already return the cash overpaid and handled interest shortfall
        # now assume there is cash left over for making principal payments
        if cash_left:
            if self._mode == 'Sequential':  # when mode is sequential
                # cycle through each tranche in order of subordination (this list is already sorted)
                # in the Sequential mode, cycle through each tranche (in order of subordination)
                # making the maximum principal payment
                for tranche in self._trancheList:
                    if tranche.notionalBalance:
                        cash_left = tranche.makePrincipalPayment(cash_left, dueAmount)
            elif self._mode == 'Pro Rata':
                # in the Pro Rata mode, use the percent of each tranche to allocate the principal
                # received to each one
                # already handle the wrong mode in mode getter, so no need for logging.error here
                for tranche in self._trancheList:
                    if tranche.notionalBalance:
                        # now is the minimum of principal received * tranche%
                        cash_left = tranche.makePrincipalPayment(cash_left, dueAmount * tranche.face_percent)
        self._reserveAccount = cash_left  # the extra cash goes into reserve account

    # This function will return a list of lists of the data in tranches
    def getWaterfall(self):
        res_lst = []
        for tranche in self._trancheList:
            res_lst.append([tranche.notionalBalance, tranche.interestDue, tranche.currentInterestPaid,
                            tranche.interestShortfall, tranche.currentPrincipalPaid])
        return res_lst

    # setters and getters for the modes on the object
    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, imode):
        if imode not in {'Sequential', 'Pro Rata'}:
            logging.error('Please enter a valid mode (Sequential/Pro Rata)')
        self._mode = imode

    @property
    def reserveAccount(self):  # getter for reserve amount
        return self._reserveAccount

    @property
    def trancheList(self):  # getter for the tranche list within the class
        return self._trancheList

    @trancheList.setter
    def trancheList(self, tranche_list):  # setter for the tranche list within the class
        # should pass in list
        self._trancheList = tranche_list

    # for each tranche in the structured_securities, reset them to period = 0
    def reset(self):
        self._reserveAccount = 0
        for tranche in self._trancheList:
            tranche.reset()  # call the reset() for each tranche
