from loan.loan import FixedRateLoan
from asset.asset_cars import Car
import logging


class AutoLoan(FixedRateLoan):
    def __init__(self, term, rate, face, car):
        if isinstance(car, Car):
            super(AutoLoan, self).__init__(term, rate, face, car)
        else:
            logging.error('Car attribute needs to be a Car type.')
            raise TypeError('Car attribute needs to be a Car type.')
