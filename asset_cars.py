from asset.asset_base import Asset


# currently do not have any functions inside Car class
class Car(Asset):
    def annualDeprRate(self, T=None):  # these rates could be changed depends on the real situations
        return 0.29

# more derived classes could be added later
class Lambourghini(Car):
    # override the annual depreciation rate function
    # will return a concrete number for Lambourghini
    def annualDeprRate(self, T=None):
        return 0.31


class Lexus(Car):
    # override the annual depreciation rate function
    # will return a concrete number for Lexus
    def annualDeprRate(self, T=None):
        return 0.38


class Civic(Car):
    # override the annual depreciation rate function
    # will return a concrete number for Civic
    def annualDeprRate(self, T=None):
        return 0.34
