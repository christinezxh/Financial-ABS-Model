# Asset Backed Security Modeling (ABS Modeling)

The objective of this program is to create a simple-implemented ABS model that help investors to understand the expected returns and risks involved of each customized securities. The codes structuring is to create and sell customized securities to investors, which are backed by the pool of loans.

Every structured deal consists of a pool of assets (the Loans) and a group of liabilities (the asset-backed securities). 

Since this is just to show the very basic ideas of ABS Model, only dealing with Standard Tranche (receive both interest and principal from the pool of loans). There are also two other types of tranches: Interest Only and Principal Only.

### Modeling Design Structures:

There are **six** module packages in this Model.

1) Asset

**Asset** module has FIVE classes: **Asset** (the base abstract class, no instance of Asset could be created directly), **Car** (derived class of Asset), **HouseBase **(derived class of Asset): **PrimaryHome **(derived class of HouseBase), and **VacationHome**(derived class of HouseBase).

All of the derived classes are the instances of assets, with distinct annual depreciation rate, respectively.

2. Loan

**Loan** module has EIGHT classes: **Loan **(the base class): **FixedRateLoan **(derived class of Loan), **VariableRateLoan** (derived class of Loan, with different rate over the life period); **AutoLoan **(derived class of FixedRateLoan, the loan for car asset only), **Mortgage **(base class, mortgage is for HouseBase only): **VariableMortgage** (derived class of Mortgage and VariableRateLoan), **FixedMortgage** (derived class of Mortgage and FixedRateLoan); **LoanPool** (A composition of Loan objects: list of loans are included in this class)

3. Liabilities

**Liabilities** module has THREE classes: **Tranche** (the base abstract class, no instance of Tranche could be created directly), **StandardTranche** (derived class of Tranche), and **StructuredSecurities** (A composition of Tranche objects: list of tranches are included in this class)

4. Simulations

Simulations module has FOUR global functions, each has a functionality of performing the monte simulations on the loans and securities: **runMonte** (take a LoanPool and a StructuredSecurities instance, take tolerance, and NSIM as the other two parameters); **runMonteParallel** (take a LoanPool and a StructuredSecurities instance, take tolerance, NSIM, and number of simutaneous processes as the other three parameters); **simulateWaterfall**(take a LoanPool and a StructuredSecurities instance,  NSIM as the other parameter); and **runSimulationParallel** (take a LoanPool and a StructuredSecurities instance, have NSIM, and number of simutaneous processes as the other two parameters).

simulateWaterfall() would call the global doWaterfall() in utils module, while the runSimulationParallel() will call simulateWaterfall()

runSimulationParallel() is to perform multiprocessing of the simulations in order to speed up.

runMonte() would call the normal and slower simulateWaterfall()

runMonteParallel() would call the much efficient multiprocessing runSimulationParallel()

I already put the result of my little experiements in the comment for you, but you could feel free to test the time taken, maybe try a little bit larger number of processes, you might find it getting slower again at some point.

NSIM: The number of simulations you would like to run

numProcesses: the number of simutaneous processes you would like to have for multiprocessing specifically

5. Utils

I put some useful functions here. The most important one would be **doWaterfall()**. This function will connect the LoanPool and StructuredSecurities to achieve certain functionality as comments in the codes (i.e. how long it took to pay all the securities, DIRR, AL, and ABS Rating)

### Other Important Ideas Related

Other useful functions include: **Timer** (both a Timer class and a decorator, you could use them in the most appropriate situation to time the operations) and **memoize** decorator.

example of utilization of Timer class (using a context Manager):

```python
with Timer('Minutes Timer') as timer:
  # codes...
  timer.configureTimerDisplay('min')
```



In the codes, I showed two ways of loading data from the csv, one with newly created codes, and one with the @classmethod

inside the LoanPool class (both work and you could play with it)



Some useful background knowledges with ABS Modeling:

The **DIRR** is quoted in basis points (BPS). One basis point is 1/100 of a percent. 10,000 basis points is 100%

(which is rated Ca in the below table). You may need to convert your DIRR to basis points to match.

Here's the rating table I used, but there might be other reference table too, depends on what you are looking for.



**TWO RISKS INVOLVED:**

1. Default risk: the risk that a lender takes on in the chance that a borrower will be unable to make the required payments on their debt obligation. Lenders and investors are exposed to default risk in virtually all forms of credit extensions. 

2. Prepayment risk:  the risk involved with the premature return of principal on a [fixed-income security](https://www.investopedia.com/terms/f/fixed-incomesecurity.asp). When debtors return part of the principal early, they do not have to make interest payments on that part of the principal. That means investors in associated fixed-income securities will not receive interest paid on the principal.

(from Investopedia.com)



#### Some of useful Waterfall metrics being used (to help investors analyze the securities to make decisions):

1. ***Internal Rate of Return (IRR)*:** This is the interest rate that results in the present value of all (monthly)

cash flows being equal to the initial investment amount

2. ***Average Life (AL):*** When playing around with your Waterfall code, you may have noticed that some

   tranches get paid down (0 balance) quicker than others, while some never get fully paid down at all. The

   AL of the security is the average time that each dollar of its unpaid principal remains unpaid. 

3. ***Reduction in Yield (DIRR)***: This is the tranche rate less the annual IRR. Essentially, the annual tranche

   rate is the annualized rate of return that the investor expects to earn whereas the IRR is the realized

   return.



#### Acknowledgement:

This is the case study from *2020 Quantnet.com*

All the codes and low-level class deisgn are written by me while the high-level design idea is from Quantnet.com
