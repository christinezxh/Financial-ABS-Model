from asset.asset_base import Asset


class HouseBase(Asset):
    pass


class PrimaryHome(HouseBase):
    # override the annual depreciation rate function
    # will return a concrete number for Primary Home
    def annualDeprRate(self, T=None):
        return 0.0363


class VacationHome(HouseBase):
    # override the annual depreciation rate function
    # will return a concrete number for Vacation Home
    def annualDeprRate(self, T=None):
        return 0.0211
