from loan.loan_pool import LoanPool
from liabilities.structured_securities import StructuredSecurities
from liabilities.tranche_base import Tranche
import logging

'''
The Waterfall tracks all the cashflows through each time period.
The pool of loans (of the assets) will provide a monthly cashflow that results from the individual
loan monthly payments. The cashflow is allocated to each of tranches in the StructuredSecurities 
in the liabilities module
'''


# This function will connect the LoanPool and Structured Securities to achieve certain functionality
def doWaterfall(loanpool, structured_securities):
    if not isinstance(loanpool, LoanPool) or not isinstance(structured_securities, StructuredSecurities):
        logging.error('Please enter the correct class type')
    loan_pool_waterfall = []  # this will be to save the info
    structured_securities_waterfall = []
    reserve_account = []
    T = 0  # start to loop from the timer period =0
    # we would like it keeps going until the LoanPool has no more active loans
    while loanpool.activeLoanCount(T) > 0:
        if T == 0:  # if at period 0, no payments should be made, just append the original data
            loan_pool_waterfall.append(loanpool.getWaterfall(T))
            structured_securities_waterfall.append(structured_securities.getWaterfall())
            reserve_account.append(0)
            structured_securities.increaseTimePeriod()  # this will increase for all the tranches
            T += 1  # increase time period for the loan pool
        # ask the LoanPool for its total payment for the current time period
        cash_amount = loanpool.paymentDue(T)  # the cash available is the total monthly payments of the loans
        # check if there's any recovery value because of the defaulted loans
        recovery_val = loanpool.checkDefaults(T)
        # now make the payment, also add the recovery value to the cash amount (part c)
        structured_securities.makePayments(cash_amount + recovery_val, loanpool.principalDue(T))
        # append the result to the structure securities waterfall by calling getWaterfall on the class
        structured_securities_waterfall.append(structured_securities.getWaterfall())
        # append the result to the loan pool waterfall by calling getWaterfall on the class
        loan_pool_waterfall.append(loanpool.getWaterfall(T))
        reserve_account.append(structured_securities.reserveAccount)
        # now increase the current period
        structured_securities.increaseTimePeriod()  # this will increase for all the tranches
        T += 1  # increase time period for the loan pool

    # initialize three lists of list with the length of number of tranches
    principal_payment = [[] for i in range(len(structured_securities.trancheList))]
    monthly_payment = [[] for i in range(len(structured_securities.trancheList))]
    metrics = [[] for i in range(len(structured_securities.trancheList))]
    # now use for loop to flatten the structured_securities_waterfall (different periods are different lists)
    for period in structured_securities_waterfall:
        for index, tranche_waterfall in enumerate(period):  # the index indicates the index of each tranche
            # sum the principal payment of each tranche separately
            principal_payment[index].append(tranche_waterfall[4])
            # sum the monthly payment = principal payment + interest payment of each tranche separately
            monthly_payment[index].append(tranche_waterfall[2] + tranche_waterfall[4])
    # enumerate the tranche, to make sure store the correct metrics for each tranche
    for index, tranche in enumerate(structured_securities.trancheList):
        metrics[index].append(tranche.IRR(monthly_payment[index]))
        metrics[index].append(tranche.DIRR(monthly_payment[index]))
        metrics[index].append(tranche.AL(principal_payment[index]))  # remember only AL uses principal payment
        metrics[index].append(Tranche.DIRR_Rating(tranche.DIRR(monthly_payment[index])))

    # after the loop is done, return all the results, as well as any amount left in reserve account
    return loan_pool_waterfall, structured_securities_waterfall, reserve_account, metrics
