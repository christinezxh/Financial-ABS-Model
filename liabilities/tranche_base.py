"""
The Tranche will be an abstract base class; no Tranche object should be created
"""
import numpy_financial as npf
import math
import numpy as np
from functools import reduce


class Tranche(object):
    def __init__(self, face, rate, face_percent, subordination):
        # initialize with face val, rate, percent of the total notional, and subordination flag
        self._face = face
        self._rate = rate
        self._face_percent = face_percent
        # face percent is the percentage taken by this tranche in structured securities
        self._subordination = subordination  # this is the order sorted; 0 would go before 1

    def makePrincipalPayment(self, PMT, dueAmount):
        raise NotImplementedError()  # make it abstract

    def makeInterestPayment(self, PMT):
        raise NotImplementedError()  # make it abstract

    # The internal rate of return that helps investor to analyze
    def IRR(self, monthlyPMT):
        # monthlyPMT will be a list of monthly payment
        # multiply by 12 to annualize the IRR
        return npf.irr([-self.face] + monthlyPMT) * 12

    # Reduction in principal_payment, specifies how much the investor lost out on
    def DIRR(self, monthlyPMT):
        return self.rate - self.IRR(monthlyPMT)

    # average life(AL) is the average time that each dollar of its unpaid principal remains unpaid
    # This is important for investors, to get a sense of how long it will take them to recoup their principal
    def AL(self, principal_payment):
        payment_periods = [i for i in range(len(principal_payment))]
        return reduce(lambda al, period_payment: al + period_payment[0] * period_payment[1],
                      zip(payment_periods, principal_payment), 0) / self.face

    # This method will translate a DIRR value to a letter rating
    # I changed this to a class method after playing around with monte, to ensure flexibility
    # because we are simply use DIRR to convert to a letter, so no need to calculate DIRR again
    @classmethod
    def DIRR_Rating(cls, DIRR):
        abs_rating = {0.06: 'Aaa', 0.67: 'Aa1', 1.3: 'Aa2', 2.7: 'Aa3', 5.2: 'A1', 8.9: 'A2', 13: 'A3', 19: 'Baa1',
                      27: 'Baa2', 46: 'Baa3', 72: 'Ba1', 106: 'Ba2', 143: 'Ba3', 183: 'B1', 231: 'B2', 311: 'B3',
                      2500: 'Caa', 10000: 'Ca'}
        # 10,000 basis points is 100% or 1
        # using generator expression
        # return the min of the rating larger than the DIRR, for example, 6.8 will return A2
        if float(DIRR) * 10000 > 0.06:
            required_key = max(rating for rating in abs_rating.keys() if float(DIRR) * 10000 >= rating)
            return abs_rating[required_key]  # return the rate by using key to retrieve the val in dict
        else:
            return abs_rating[0.06]  # if DIRR is smaller tahn 0.06, treat it as if 0.06

    # class level function to calculate yield for each tranche
    @classmethod
    def calculateYield(cls, dirr, al):
        return (7 / (1 + 0.08 * math.exp(-0.19 * al / 12.0)) + 0.019 * math.sqrt(al * dirr * 100 / 12.0)) / 100.0

    # function to calculate the new tranche rate for the runMonte
    # based on the old tranche rates,, coeff, and yields for each tranche
    @classmethod
    def newTrancheRate(cls, oldTrancheRate, coeff, yields):
        return oldTrancheRate + coeff * (yields - oldTrancheRate)

    # function to update the difference for monte carlo simulation
    # will be used to compare with the tolerance
    @classmethod
    def diff(cls, percent, last_rates, new_rates):
        step1 = [x - y for x, y in zip(last_rates, new_rates)]
        step2 = [abs(x / y) for x, y in zip(step1, last_rates)]
        return np.dot(percent, step2)  # np.dot allow us to add the previous tranche's result with the next one's
        # Formula: (nA*|(lastA_Rate - newA_Rate)/lastA_Rate| + nB*|(lastB_Rate - newB_Rate)/lastB_Rate|)/total_face
        # so instead of passing the face value for both A and B, I could just use nA/total_face = percent of A
        # same thing for B

    # setter and getter functions for the above class member
    @property
    def face(self):
        return self._face

    @face.setter
    def face(self, iface):
        self._face = iface

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, irate):
        self._rate = irate

    @property
    def subordination(self):
        return self._subordination

    @property
    def face_percent(self):
        return self._face_percent
