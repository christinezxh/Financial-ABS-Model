class Asset(object):
    def __init__(self, value):
        self._initialValue = value

    def annualDeprRate(self, T=None):
        raise NotImplementedError()  # make it abstract

    # This ensures that no one can directly instantiate an Asset object

    def monthlyDeprRate(self, T=None):
        return self.annualDeprRate() / 12

    def value(self, T):
        return self._initialValue * (1 - self.monthlyDeprRate()) ** T

    # getter and setter functions for the class Asset
    @property
    def initialValue(self):
        return self._initialValue

    @initialValue.setter
    def initialValue(self, i_initialValue):
        self._initialValue = i_initialValue
