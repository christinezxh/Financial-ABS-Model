from asset.asset_base import Asset
import logging
from utils.memoize import Memoize
from datetime import datetime, timedelta


class Loan(object):
    # the initializing function to initialize our member data
    def __init__(self, term, rate, face, asset):
        if isinstance(asset, Asset):
            self._asset = asset
        else:
            # log an error prior to raising the exception.
            logging.error('Asset attribute needs to be an Asset type.')
            raise TypeError('Asset attribute needs to be an Asset type.')
        self._term = term
        self._rate = rate
        self._face = float(face)
        self._default = False

    # This static-level method will return the monthly interest rate for a passed-in annual rate
    @staticmethod
    def monthlyRate(annualRate):
        return annualRate / 12

    # This static-level method will return the annual interest rate for a passed-in monthly rate
    @staticmethod
    def annualRate(monthlyRate):
        return monthlyRate * 12

    # This is the class-level method to calculate monthly payment
    @classmethod
    def calcMonthlyPmt(cls, term, rate, face):
        if rate > 0:  # if rate is not zero, calculate monthly payment
            # logging.debug('Monthly payment = monthly rate * face / (1-(1+monthly rate))^-term')
            return (Loan.monthlyRate(rate) * face) / (1 - (1 + Loan.monthlyRate(rate)) ** -term)
        else:
            return 0

    # This is the class-level method to calculate remaining balance at period T
    @classmethod
    def calcBalance(cls, term, rate, face, T):
        # if the period entered is larger than the term of the loan
        # simply return 0
        if T > term or T < 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            logging.info('Entered T is greater than term')
            return 0
        elif T == 0:
            return face
        else:
            step1 = face * pow((1 + Loan.monthlyRate(rate)), T)
            # logging.debug('calculating the FV of face')
            # here we call the class-level method to calculate the monthly payment
            step2 = cls.calcMonthlyPmt(term, rate, face) * (
                    (pow((1 + Loan.monthlyRate(rate)), T) - 1) / Loan.monthlyRate(rate))
            balance = step1 - step2
            # logging.debug('calculating the FV of annuity')
            # logging.debug(f'calculating the balance at at T = {T}: {balance} = {step1} (FV of face) - {step2} (FV of '
            #               f'annuity)')
            return balance

    # this is the object-level method to calculate monthly payment
    # delegate to the class-level method calcMonthlyPmt
    def monthlyPayment(self, period):
        # display info level if entered T is greater than term
        # a friendly info to the user
        if period > self.term or self._default:
            logging.info('Entered T is greater than term')
            return 0
        else:
            return self.calcMonthlyPmt(self.term, self.getRate(period), self._face)
        # input the three data members in Loan class

    # total payments = the sum of monthly payments
    # still use the object-level method for calculation
    def totalPayments(self):
        # the monthly payment might be different depending on the period instead of simply multiplying it by term,
        # I chose to sum up each payment individually by using comprehension
        return sum(self.monthlyPayment(t) for t in range(self.term))

    # total interest would be calculated as total payments - principal(face) value
    def totalInterest(self):
        return self.totalPayments() - self._face

    # This function will calculate the interest due at time T
    def interestDue(self, T):
        if T > self.term or T <= 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            # logging.info('Entered T is greater than term')
            return 0  # if T entered is larger than the term or <= 0, return 0
        else:
            return Loan.monthlyRate(self.getRate(T)) * self.balance(T - 1)

    # This function will calculate the principal due at time T
    def principalDue(self, T):
        if T > self.term or T <= 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            # logging.info('Entered T is greater than term')
            return 0  # if T entered is larger than the term or <= 0, return 0
        else:
            principal_due = self.monthlyPayment(T) - self.interestDue(T)
            # logging.debug(
            #     f'calculating the principal due at T = {T}: {principal_due} = {self.monthlyPayment(T)} (monthly '
            #     f'payment) -  {self.interestDue(T)} (interest due)')
            return principal_due

    # This is the object level method to calculate the remaining balance at period T
    # delegate to the class level method calcBalance()
    def balance(self, T):
        # If the loan is defaulted, a flag should be set on the object and the
        # balance becomes 0.
        if self._default:
            return 0  
        return self.calcBalance(self.term, self.getRate(T), self._face, T)

    # This function will handle the rate in a dictionary
    def getRate(self, T):
        # if the period entered is larger than the term of the loan
        # simply return 0
        if 0 < T <= self.term:
            return self._rate
        else:
            return 0

    default_dict = {1: 0.0005, 11: 0.001, 60: 0.002, 120: 0.004, 180: 0.002, 210: 0.001}

    # This method will determine whether the loan defaults
    def checkDefault(self, num):
        if num == 0:
            self._default = True

    # This method should return the
    # current asset value for the given period, times a recovery multiplier
    def recoveryValue(self, T):
        recovery_value = self._asset.value(T) * 0.6
        # logging.debug(
        #     f'calculating the recovery value at T = {T}: {recovery_value} = asset value {self._asset.value(T)} * '
        #     f'recovery multiplier 0.6')
        return recovery_value

    # This should return the available equity (the asset value less the loan balance)
    def equity(self, T):
        # equity should not go below 0
        m_equity = self._asset.value(T) - self.balance(T)
        if m_equity > 0:
            logging.debug(f'calculating the equity at T = {T}: {m_equity} = asset value {self._asset.value(T)} - '
                          f'loan balance {self.balance(T)}')
            return m_equity
        else:  # so if it returns a negative value, just return 0
            logging.debug(f'equity at time T = {T} is smaller than 0')
            return 0

    # Below are the recursive versions of the functions
    def interestDueRecursive(self, T):
        if T > self.term or T <= 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            logging.info('Entered T is greater than term')
            return 0  # if T entered is larger than the term of loan, return 0
        else:
            logging.warning('Recursive functions might take a long time, explicit versions are recommended')
            return self.interestDueRecursiveOutput(T)

    # the output function is for calculations inside the class, the user will not use this
    # will be called by the interestDueRecursive() to return the calculations
    @Memoize
    def interestDueRecursiveOutput(self, T):
        return Loan.monthlyRate(self.getRate(T)) * self.balanceRecursiveOutput(T - 1)

    def principalDueRecursive(self, T):
        if T > self.term or T <= 0:
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
        return self.monthlyPayment(T) - self.interestDueRecursiveOutput(T)

    def balanceRecursive(self, T):
        if T > self.term or T < 0:
            # display info level if entered T is greater than term
            # a friendly info to the user
            logging.info('Entered T is greater than term')
            return 0  # if T entered is larger than the term of loan, return 0
        else:
            logging.warning('Recursive functions might take a long time, explicit versions are recommended')
            return self.balanceRecursiveOutput(T)

    # the output function is for calculations inside the class, the user will not use this
    # will be called by the balanceRecursive() to return the calculations
    @Memoize
    def balanceRecursiveOutput(self, T):
        if T == 0:
            return self._face
        else:
            return self.balanceRecursiveOutput(T - 1) - self.principalDueRecursiveOutput(T)

    # below are the getters and setters functions for these data members

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, iterm):
        self._term = iterm

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, irate):
        self._rate = irate

    @property
    def face(self):
        return self._face

    @face.setter
    def face(self, iface):
        self._face = iface

    @property
    def default_status(self):
        return self._default

    @default_status.setter
    def default_status(self, idefault_status):
        self._default = idefault_status

    # a reset function to set the default state back to false
    def reset(self):
        self._default = False
