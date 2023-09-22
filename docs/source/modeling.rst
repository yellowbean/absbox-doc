Modelling
***********

.. autosummary::
   :toctree: generated

Deal modeling is a process to build deal class with descriptive components follows:

* Asset info -> pool asset attributes, loan by loan or repline level data or projected cashflow as input
* Bond info -> bonds with different types and equity tranche
* Waterfall info -> Describe the priority of payments when:
    * End of pool collection (Optional)
    * Distribution day for all the bonds and fees 
    * Event of Default (Optional)
    * Clean up call (Optional)
* Dates info
  * Cutoff day / Closing Date / Next / First payment Date or series of custom dates
* Triggers (Optional) -> describe what may happened then what state changed should be performed in deal
* Liquidity Provider (Optional) -> entities provides interest bearing/non-bearing support to shortfall of fee/interest or bond principal
* Hedges (Optional) -> interest rate swap/ fx swap


Structure of a `Generic` deal 

.. code-block:: python

    from absbox.local.generic import Generic
    
    generalDeal = Generic(
        "Deal Name/Description"
        ,<Dates>
        ,<Asset/Pool Info>
        ,<Account info>
        ,<Bonds Info>
        ,<Fee Info>
        ,<Waterfall Info>
        ,<Collection Rule>
        ,<Call settings>
        ,<liquidation facilities>
        ,<custom data/formula>
        ,<triggers>
    )

.. _Generic ABS:

|:new:| Now we have a map-based syntax suguar ``mkDeal`` to create a deal without remembering the order of arguments passed into `Generic` class ! 

.. code-block:: python
  
    name = "TEST01"
    dates = {"cutoff":"2021-03-01","closing":"2021-06-15","firstPay":"2021-07-26"
        ,"payFreq":["DayOfMonth",20],"poolFreq":"MonthEnd","stated":"2030-01-01"}
    pool = {'assets':[["Mortgage"
            ,{"originBalance":2200,"originRate":["fix",0.045],"originTerm":30
              ,"freq":"Monthly","type":"Level","originDate":"2021-02-01"}
              ,{"currentBalance":2200
              ,"currentRate":0.08
              ,"remainTerm":20
              ,"status":"current"}]]}
    accounts = {"acc01":{"balance":0}}
    bonds = {"A1":{"balance":1000
                ,"rate":0.07
                ,"originBalance":1000
                ,"originRate":0.07
                ,"startDate":"2020-01-03"
                ,"rateType":{"Fixed":0.08}
                ,"bondType":{"Sequential":None}}
            ,"B":{"balance":1000
                ,"rate":0.0
                ,"originBalance":1000
                ,"originRate":0.07
                ,"startDate":"2020-01-03"
                ,"rateType":{"Fixed":0.00}
                ,"bondType":{"Equity":None}
                }}
                
    waterfall = {"amortizing":[
                    ["accrueAndPayInt","acc01",["A1"]]
                    ,["payPrin","acc01",["A1"]]
                    ,["payPrin","acc01",["B"]]
                    ,["payPrinResidual","acc01",["B"]]
                ]}
    collects = [["CollectedInterest","acc01"]
                ,["CollectedPrincipal","acc01"]
                ,["CollectedPrepayment","acc01"]
                ,["CollectedRecoveries","acc01"]]

    deal_data = {
        "name":name
        ,"dates":dates
        ,"pool":pool
        ,"accounts":accounts
        ,"bonds":bonds
        ,"waterfall":waterfall
        ,"collect":collects
    }

    from absbox import mkDeal
    d = mkDeal(deal_data)  ## now a generic class created



Building Blocks 
==================

`Generic` is a class that represent `SPV` which contains the dates/liabilities/assets/waterfall/trigger/hedge information.

.. code-block:: python
    
    from absbox.local.generic import Generic


There are 5 reusable building blocks: ``<DatePattern>``, ``<Formula>``, ``<Condition>``, ``<Curve>``, ``<Pricing Method>``, all of them are being used in different components.


DatePattern
-------------

``<DatePattern>`` is used to describe a series of dates .

* ``"MonthFirst"``  -> Every Jun 1, May 1 during the projection
* ``"MonthEnd"``  ->Every  Month End ,like Jan 31, Feb 28/29  during the projection
* ``"QuarterFirst"`` -> Every March 1 , Jun 1 , Sep 1 , Dec 1 during the projection
* ``"QuarterEnd"``  -> Every March 31, Jun 30, Sep 30, Dec 31 during the projection
* ``"YearFirst"`` -> Every Jan 1 during the projection
* ``"YearEnd"`` -> Every Dec 31 during the projection
* ``["MonthDayOfYear",M,D]`` -> Every a day of the year , like Feb 14 on every year during the projection
* ``["DayOfMonth",M]`` -> A day of the month , like 15 on each month during the projectionh
* ``["CustomDate","YYYY-MM-DD1","YYYY-MM-DD2"]`` -> a series of user defined dates
* ``["EveryNMonth","YYYY-MM-DD",N]`` -> a seriers day starts with "YYYY-MM-DD", then every other N months afterwards

Composite ``<DatePattern>``

DatePatterns can be composed together:

* ``["After","YYYY-MM-DD",<datepattern>]`` -> a <datapattern> after "YYYY-MM-DD"(exclusive)
* ``["AllDatePattern",<datepattern1>,<datepattern2>.....]`` -> a union set of date pattern during the projection, like sum of dates
* ``["ExcludeDatePattern",<datepattern1>,<datepattern2>.....]`` -> build dates from 1st <datepattern1> and exclude dates from <datepattern2>，<datepattern3>... 
* ``["OffsetDateDattern",<datepattern>,N]`` ->  build dates from <datepattern> and offset days by N ( positive N move dates to future) , negative N will move dates to past ) 

Formula 
---------

Structured product is using ``formula`` to define the amount of account transfer, principal paydown or fee pay limit etc.

``absbox`` use the concept of ``formula`` in an extreamly composible way, a ``formula`` can be a variable reference to deal attributes.

* Bond 
    * ``("bondBalance",)`` -> sum of all bond balance
    * ``("bondBalance","A","B")`` -> sum of balance of bond A and bond B
    * ``("originalBondBalance",)`` -> bond balance at issuance
    * ``("bondFactor",)``  -> bond factor
    * ``("bondDueInt","A","B")``  -> bond due interest for bond A and bond B
    * ``("lastBondIntPaid","A")``  -> bond last paid interest
    * ``("behindTargetBalance","A")``  -> difference of target balance with current balance for the bond A
    * ``("monthsTillMaturity","A")``  -> number of months till the maturity date of bond A
    * ``("bondTxnAmt", None,"A")``  -> Total transaction amount of bond 'A'
    * ``("bondTxnAmt", "<PayInt:A>","A")``  -> Total transaction amount of interest payment bond 'A'
* Pool 
    * ``("poolBalance",)``  -> current pool balance
    * ``("originalPoolBalance",)``  -> pool original balance 
    * ``("currentPoolDefaultedBalance",)``  -> pool defaulted balance 
    * ``("cumPoolDefaultedBalance",)``  -> pool cumulative defaulted balance 
    * ``("cumPoolRecoveries",)`` -> pool cumulative recoveries
    * ``("poolFactor",)`` -> pool factor
    * ``("borrowerNumber",)`` -> number of borrower
* Accounts
    * ``("accountBalance",)`` -> sum of all account balance
    * ``("accountBalance","A","B")`` -> sum of account balance for "A" and "B"
    * ``("reserveGap","A","B")`` -> sum of shortfall of reserve amount of specified accounts
    * ``("accountTxnAmt",None,"A")`` -> total transaction amount of account "A"
    * ``("accountTxnAmt","<tag>","A")`` -> total transaction amount tagged with ``<tag>`` of account "A"
* Expense
    * ``("feeDue","F1","F2")`` -> sum of fee due for fee "F1","F2"
    * ``("lastFeePaid","F1","F2")`` -> sum of fee last paid for fee "F1","F2"
    * ``("feeTxnAmt",None,"A")`` -> total transaction amount of fee "A"
* LiquidationProvider 
    * ``("liqCredit","F1","F2")`` -> sum of credit provided by "F1" "F2"


Or `formula` can be an arithmetic calculation on itselfies.

* Combination
    * ``("factor", <Formula>, <Number>)`` -> multiply <Number> to a formula
    * ``("Max", <Formula>, <Formula>, ...)`` -> get the higher value in the list
    * ``("Min", <Formula>, <Formula>, ...)`` -> get the lower value in the list
    * ``("sum", <Formula>, <Formula>, ...)`` -> sum of formula value
    * ``("substract", <Formula>, <Formula>, ...)`` -> using 1st of element to substract rest in the list
    * ``("floorWith", <Formula1> , <Formula2>)`` -> get value of <formula1> and floor with <formula2>
    * ``("floorWithZero", <Formula> )`` -> get value of <formula1> and floor with 0
    * ``("floorCap", <Formula1>, <Formula2>, <Formula3> )`` -> use <Formula1> as floor, <Formula2> as cap, and use <Formula3> as value
    * ``("capWith", <Formula1> , <Formula2>)`` -> get value of <formula1> and cap with <formula2>
    * ``("constant", <Number>)``  -> a constant value
    * ``("custom", <Name of user define data>)`` -> use a custom data

`formula` can be used to refer to  Integer/Bool/Ratio type data as well

* Integer 
    * ``("borrowerNumber",)`` -> number of borrower
* Ratio
    * ``("bondFactor",)`` -> factor of bond
    * ``("poolFactor",)`` -> factor of pool
    * ``("cumulativePoolDefaultRate",)`` -> cumulative default rate of pool
* Bool 
    * ``("trigger", loc ,idx)`` -> trigger with index at ``idx`` at ``loc`` status ->


Condition
------------

condition is a `boolean` type test

* it can be set up in reserve account to define different target reserve amount;
* or in the waterfall to run the distribution action only when the testing is passing;
* or it can be used in trigger to describle whether it will be triggered or not.

There are couple type of ``Condition`` to perform :

Compare with a number 
^^^^^^^^^^^^^^^^^^^^^^^

* ``[<formula>,">",val]`` -> true when <formula> greater than a value
* ``[<formula>,"<",val]`` -> true when <formula> less than a value
* ``[<formula>,">=",val]`` -> true when <formula> greater or equals to a value
* ``[<formula>,"<=",val]`` -> true when <formula> less or equals than a value
* ``[<formula>,"=",val]`` -> true when <formula> equals to a value

Compare with a curve
^^^^^^^^^^^^^^^^^^^^^^^^

* ``[<formula>,">",curve]`` -> true when <formula> greater than a curve
* ``[<formula>,"<",curve]`` -> true when <formula> less than a curve
* ``[<formula>,">=",curve]`` -> true when <formula> greater or equals to a curve
* ``[<formula>,"<=",curve]`` -> true when <formula> less or equals than a curve
* ``[<formula>,"=",curve]`` -> true when <formula> equals to a curve

Date Based Condition
^^^^^^^^^^^^^^^^^^^^
* ``["<",date]`` -> before certain date
* ``[">",date]`` -> after certain date
* ``["<=",date]`` -> On or beore certain date
* ``[">=",date]`` -> On or after certain Date

Deal Status 
^^^^^^^^^^^^^^^^^^^^
* ``["status", "Amortizing"]`` -> true if current status is `Amortizing`
* ``["status", "Revolving"]`` -> true if current status is `Revolving`
* ``["status", "Accelerated"]`` -> true if current status is `Accelerated`
* ``["status", "Defaulted"]`` -> true if current status is `Defaulted`
* ``["status", "PreClosing"]`` -> true if current status is `PreClosing`
* ``["status", "Ended"]`` -> true if current status is `Ended`


Nested Condition
^^^^^^^^^^^^^^^^^^^^
* ``["all",<condition>,<condition>]`` -> true if all of <condition> is true
* ``["any",<condition>,<condition>]`` -> true if any of <condition> is true

Curve
----------
``Curve`` was an abstract type of a series time-depend data points, which are being used in couple components:

* Bond Schedule Amortization balance
* Interest Rate assumpition 
* An curve for tartget reserve balance for account
* Threshold curve for trigger , like cumulative default rate
* A curve in custom data component.

To build a ``Curve`` , just a list of 2-element list 

.. code-block:: python

  ``[["2022-01-01",150],["2022-02-01",200]]``

Pricing Method
----------------
``<Pricing Method>`` was an annotation used to price an ``Asset`` when waterfall action trying to liquidate assets or buy revolving assets.

there are couple ways of pricing

* Pricing by current balance 

  * ``["Current|Defaulted", a, b]``  -> Applies ``a`` as factor to current balance of a performing asset; ``b`` as factor to current balance of a defaulted asset
  * ``["Cuurent|Delinquent|Defaulted", a, b, c]`` -> same as above ,but with a ``b`` applies to an asset in deliquency.
  * ``["PV|Defaulted", a, b]`` ->  using ``a`` as pricing curve to discount future cashflow of performing asset while use ``b`` as factor to current balance of defautled asset.

* Pricing by PV of future cashflow of assets 

  * ``["PVCurve", ts]`` -> using `ts` as pricing curve to discount future cashflow of all assets.

Components
============

Deal Dates
------------

Depends on the status of deal, the dates shall be modeled either in ``ongoing`` or ``preclosing``

if it is ``preclosing`` stage ( the deal has not been issued yet )

- ``cutoff``: All pool cashflow after `Closing Date` belongs to the SPV
- ``closing``:  after `Closing Date` belongs to the SPV
- ``Settle Date`` : Bond start to accrue interest after `Settle Date`.
- ``firstPay``: First execution of payment waterfall
- ``stated`` : legal maturity date of the deal.
- ``poolFeq`` : a :ref:`DatePattern`, describle the dates that collect cashflow from pool
- ``payFeq`` : a :ref:`DatePattern`, describle the dates that distribution funds to fees and bonds.

.. code-block:: python

    {"cutoff":"2022-11-01"
    ,"closing":"2022-11-15"
    ,"firstPay":"2022-12-26"
    ,"stated":"2030-01-01"
    ,"poolFreq":"MonthEnd"
    ,"payFreq":["DayOfMonth",20]}


if deal is `ongoing` ( which has been issued ), the difference is that in `preclosing` mode, the projection will include an event of `OnClosingDate` which describe a sequence of actions to be performed at the date of `closing`

- ``collect`` : ["last pool collection date","next pool collection date"]
- ``pay`` : ["last distribution payment date","next distribution payment date"]
- ``poolFeq`` : a :ref:`DatePattern`, describle the dates that collect cashflow from pool
- ``payFeq`` : a :ref:`DatePattern`, describle the dates that distribution funds to fees and bonds.

.. code-block:: python

    {"collect":["2022-11-01"   # last pool collection date,
                ,"2022-12-01"] # next pool collection date
    ,"pay":["2022-11-15"   # last distribution payment date,
            ,"2022-12-15"] # next distribution date 
    ,"stated":"2030-01-01"
    ,"poolFreq":"MonthEnd"
    ,"payFreq":["DayOfMonth",20]
    }


Custom Defined Dates
^^^^^^^^^^^^^^^^^^^^^
User are free to feed in a series of custom defined pool collection date / bond payment dates to accomodate holidays etc.

.. code-block:: python

   {"poolCollection":["2023-01-31","2023-02-28"...]
   ,"distirbution":["2023-02-01","2023-03-01"...]
   ,"cutoff":"2022-11-21"
   ,"closing":"2023-01-01"}


Fee/Expenses
--------------

syntax: ``({fee name} , {fee description} )``, fees fall into types below :

one-off fee
^^^^^^^^^^^^^^^^^^

with a oustanding balance and will be paid off once it paid down to zero

.. code-block:: python
  
  ("issuance_fee"
      ,{"type":{"fixFee":100}})

recurrance fee
^^^^^^^^^^^^^^^^

a fix amount fee which occurs by defined :ref:`Date Pattern`

.. code-block:: python
  
   ,("rating_fee"
    ,{"type":{"recurFee":[["MonthDayOfYear",6,30],15]}})



percentage fee
^^^^^^^^^^^^^^^^^^^
pecentage fee, a fee type which the due amount depends on a percentage of :ref:`Formula`

like a fee is base on 

  * percentage of `pool balance`
  * a percentage of pool collection `interest`
  * a higher/lower amount of two `formula`
  * a sum of `formula` 
  * ...

.. code-block:: python
  
  ("bond_service_fee"
      ,{"type":{"pctFee":["bondBalance",0.02]}})


annualized fee
^^^^^^^^^^^^^^^^

similar to `percentage fee` but it will use an annualized rate to multiply the value of :ref:`Formula`.
either reference to pool balance  or bond balance , etc.... it will accure type fee, which if not being paid, it will increase the due amount.

.. code-block:: python
  
  ("servicer_fee"
      ,{"type":{"annualPctFee":["poolBalance",0.02]}})


custom fee flow
^^^^^^^^^^^^^^^^^^^

A user defined time series expenses, the date and amount can be customized.

like 100 USD at 2022-1-20 and incur other 20 USD at 2024-3-2

.. code-block:: python
  
   ,("irregulargfee"
    ,{"type":{"customFee":[["2024-01-01",100]
                          ,["2024-03-15",50]]}})


count type fee
^^^^^^^^^^^^^^^^^^^

the fee due equals to a number multiply a unit fee. The number is a formula reference.

.. code-block:: python
  
   ,("borrowerFee"
    ,{"type":{"numFee":[["DayOfMonth",20],("borrowerNumber",),1]}}



Pool
---------

``Pool`` represents a set of assets ,which generate cashflows to support expenses and liabilities.

* it can either has a loan level ``asset`` or ``projected cashflow``
* other optional fields like ``issuance balance``, which will be supplimental to calculate certain value , like ``Pool Factor``

Mortgage
^^^^^^^^^^^

`Mortgage` is a loan with level pay at each payment period.

`type` field can be used to define either its `Annuity` type or `Linear` Type

* `Level` -> `Annuity`,`French`
* `Even` -> `Linear`

.. code-block:: python

  ["Mortgage"
    ,{"originBalance": 12000.0
      ,"originRate": ["fix",0.045]
      ,"originTerm": 120
      ,"freq": "Monthly"
      ,"type": "Level"
      ,"originDate": "2021-02-01"}
    ,{"currentBalance": 10000.0
      ,"currentRate": 0.075
      ,"remainTerm": 80
      ,"status": "Current"}]

ARM 
^^^^^^^^

`ARM` is a type of `Mortgage` that has one more field `arm` to describe the rate adjust behavior of the loan.

* initPeriod -> Required
* firstCap -> Optional
* periodicCap -> Optional
* lifeCap -> Optional
* lifeFloor -> Optional


.. code-block:: python


    ["AdjustRateMortgage"
    ,{"originBalance": 240.0
      ,"originRate": ["floater"
                      ,0.03
                      ,{"index":"LIBOR1M"
                        ,"spread":0.01
                        ,"reset":["EveryNMonth","2023-11-01",2]}]
      ,"originTerm": 30 ,"freq": "monthly","type": "level"
      ,"originDate": "2023-05-01"
      ,"arm":{"initPeriod":6,"firstCap":0.015,"periodicCap":0.01,"lifeCap":0.1,"lifeFloor":0.15} }
    ,{"currentBalance": 240.0
      ,"currentRate": 0.08
      ,"remainTerm": 19
      ,"status": "current"}]

Loan
^^^^^^^^^^
`Loan` is type of asset which has interest only and a lump sum principal payment at end


.. code-block:: python


  ["Loan"
    ,{"originBalance": 80000
      ,"originRate": ["floater",0.045,{"index":"SOFR3M"
                                      ,"spread":0.01
                                      ,"reset":"QuarterEnd"}]
      ,"originTerm": 60
      ,"freq": "SemiAnnually"
      ,"type": "i_p"
      ,"originDate": "2021-03-01"}
    ,{"currentBalance": 65000
      ,"currentRate": 0.06
      ,"remainTerm": 48
      ,"status": "Current"}]

Lease
^^^^^^^^^

`Lease` is an asset with have evenly distributed rental as income or step up feature on the rental over the projection timeline.

.. code-block:: python

  ["Lease"
   ,{"fixRental": 12.0
    ,"originTerm": 96
    ,"freq": ["DayOfMonth",15]
    ,"originDate": "2022-01-05"
    ,"status":"Current"
    ,"remainTerm":80}]

step up type lease which rental will increase by pct after each accrue period

.. code-block:: python

  ["Lease"
    ,{"initRental": 24.0
    ,"originTerm": 36
    ,"freq": ["DayOfMonth",25]
    ,"originDate": "2023-01-01"
    ,"status":"Current"
    ,"remainTerm":30
    ,"accrue": ["DayOfMonth",1]
    ,"pct": 0.05}]

or user can specify the vector for the rental change 

.. code-block:: python

  ["Lease"
   ,{"initRental": 24.0
    ,"originTerm": 36
    ,"freq": ["DayOfMonth",25]
    ,"originDate": "2023-01-01"
    ,"status":"Current"
    ,"remainTerm":30
    ,"accrue": ["DayOfMonth",3]
    ,"pct": [0.05,0.065,0.06,-0.07]}]



Installment
^^^^^^^^^^^^^^

`Installment` is an asset which has evenly distributed fee and principal

.. code-block:: python

  ["Installment"
   ,{"originBalance": 1000.0
    ,"feeRate": ["fix",0.01]
    ,"originTerm": 12
    ,"freq": "Monthly"
    ,"type": "f_p"
    ,"originDate": "2022-01-01"}
    ,{"status": "current"
      ,"currentBalance":1000
      ,"remainTerm":10}]


Accounts
---------

There are two types of `Account`:

  * `Bank Account` -> which used to collect money from pool and pay out to fees/bonds
  * `Reserve Account` -> with one addtional attribute to `Bank Account` , specifies target reserve amount of the account

syntax   ``({account name},{account description})``, i.e


* Bank Account

.. code-block:: python

  (("principalAccount",{"balance":0})
   ,("repaymentAccount",{"balance":0}))

Reserve Account
^^^^^^^^^^^^^^^^^^

There is one extra attribute to set : `type`

  * Fix Amount： a single reserve amount 
  
    .. code-block:: python

      ("ReserveAccountA",{"balance":0
                         ,"type":{"fixReserve":1000}})

  * Formula： the target reserve amount is derived from a :ref:`Formula` , like 2% of pool balance
  
    .. code-block:: python

      ("ReserveAccountB",{"balance":0
                         ,"type":{"targetReserve":[("poolBalance",),0.015]}})

  * Nested Formula, the target reserve amount is base on higher or lower of two formula 

  * Conditional amount starts with ``When``, the target reserve amount depends on :ref:`Condition`:
    
    * certain :ref:`Formula` value is above or below certain value
    * satisfy all of :ref:`Condition` s 
    * satisfy any one of :ref:`Condition` s 
  
    .. code-block:: python

      ("ReserveAccountC",{"balance":0
                         ,"type":{"max":[
                                   {"targetReserve":[("poolBalance",),0.015]}
                                   ,{"fixReserve":100}]})

      ("ReserveAccountD",{"balance":0
                         ,"type":{"min":[
                                    {"targetReserve":[("poolBalance",),0.015]}
                                    ,{"fixReserve":100}]})

      ("ReserveAccountE",{"balance":0
                         ,"type":{"min":[
                                    {"max":[{"targetReserve":[("poolBalance",),0.015]}
                                           ,{"fixReserve":100}]}
                                    ,{"fixReserve":150}]})

      ("ReserveAccountF",{"balance":0
                         ,"type":{"when":[
                                     [("bondBalance",">",0]
                                    ,{"max":[{"targetReserve":[("poolBalance",),0.015]}
                                           ,{"fixReserve":100}]}
                                    ,{"fixReserve":150}]})

      ("ReserveAccountG",{"balance":0
                         ,"type":{"when":[
                                     ["any"
                                       ,[("bondBalance",">",0]
                                       ,[("poolFactor","<",0.5]]
                                    ,{"max":[{"targetReserve":[("poolBalance",),0.015]}
                                           ,{"fixReserve":100}]}
                                    ,{"fixReserve":150}]})

Interest/Cash Investment
^^^^^^^^^^^^^^^^^^^^^^^^^^

model the interest or short-term investment income in the account.

syntax: 

``{"period": <date Pattern>,"rate": <number>,"lastSettleDate":<date>}``

.. code-block:: python

  ("ReserveAccountA",{"balance":0
                    ,"type":{"fixReserve":1000}
                    ,"interest":{"period":"QuarterEnd"
                                 ,"rate":0.05
                                 ,"lastSettleDate":"2022-11-02"}})

  ("InvestmentAccountA",{"balance":0
                    ,"type":{"fixReserve":1000}
                    ,"interest":{"period":"QuarterEnd"
                                 ,"index":"SOFR3M"
                                 ,"spread":0.001
                                 ,"lastSettleDate":"2022-11-02"}})



Bonds/Tranches
---------------

syntax ``({bond/tranche name},{bond/tranche description})``

there are 3 types of `Interest` settings for bonds

  * Fix Rate   :code:`"rateType":{"fix":0.0569}`
  * Float Rate   :code:`"rateType":{"floater":["SOFR1Y",-0.0169,"MonthEnd"]}`
  * Step-Up Rate :code:`"rateType":{"StepUp":0.06,"Spread":0.01,"When":["After","2023-05-01","YearEnd"]}`

there are 4 types of `Principal` for bonds/tranches

  * ``Sequential``： can be paid down as much as its oustanding balance
  * ``PAC``： Balance of bond can only be paid down by a predefined schedule
  * ``Lockout``： Principal won't be paid after lockout date
  * ``Equity``：  No interest and shall serve as junior tranche

Sequential 
^^^^^^^^^^^
A bond with will receive principal till it's balance reduce to 0.

.. code-block:: python

    ("A1",{"balance":3_650_000_000
           ,"rate":0.03
           ,"originBalance":3_650_000_000
           ,"originRate":0.03
           ,"startDate":"2020-01-03"
           ,"rateType":{"Floater":["SOFAR1Y",-0.0169,"MonthEnd"]}
           ,"bondType":{"Sequential":None} })
 
PAC
^^^^^^^^^^^
A bond with target amortize balances, it will stop recieving principal once its balance hit the targeted balance 


.. code-block:: python
 
  ("A1",{"balance":1000
       ,"rate":0.07
       ,"originBalance":1000
       ,"originRate":0.07
       ,"startDate":"2020-01-03"
       ,"rateType":{"Fixed":0.08}
       ,"bondType":{"PAC":
                     [["2021-07-20",800]
                     ,["2021-08-20",710]
                     ,["2021-09-20",630]
                     ,["2021-10-20",0]
                     ]}})


Lockout
^^^^^^^^^^^
A bond with ``Lockout`` type is used to setup bond with only recieve principal after the `lockout date`

This bond only get principal repayed starting at `2021-09-20`

.. code-block:: python

  ("A1",{"balance":1000
        ,"rate":0.07
        ,"originBalance":1000
        ,"originRate":0.07
        ,"startDate":"2020-01-03"
        ,"rateType":{"Fixed":0.08}
        ,"bondType":{"Lockout":"2021-09-20"}})
 
Equity
^^^^^^^^^^^

``Equity`` type is used to model junior or equity slice of liabilites of the SPV

          
.. code-block:: python

     ,("R",{"balance":900_883_783.62
           ,"rate":0.0
           ,"originBalance":2_123_875_534.53
           ,"originRate":0.00
           ,"startDate":"2020-01-03"
           ,"rateType":{"InterimYield":0.02}  
           ,"bondType":{"Equity":None} })



Waterfall
-------------

Waterfall means a list of ``Action`` to be executed. A Deal may have more than one waterfalls.


Different Waterfalls in Deal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It was modeled as a map, with key as identifier to distinguish different type of waterfall.

* `"amortizing"` -> will be pick when deal status is `Amortizing`
* `("amortizing", "accelerated")` -> will be pick when deal status is `Accelerated`
* `("amortizing", "defaulted")` -> will be pick when deal status is `Defaulted`
* `"cleanUp"` -> will be pick when deal is being clean up call
* `"endOfCollection"` -> will be exectued at the end of collection period
* `"closingDay"` -> will be exectued at the `Day of Closing` if deal status is `PreClosing`
* `"default"` -> the default waterfall to be executed if no other waterfall applicable

.. image:: img/waterfall_in_deal_runt.png
  :width: 500
  :alt: waterfall_run_loc

ie：

.. code-block:: python

   {"amortizing":[
       ["payFee",["acc01"],['trusteeFee']]
       ,["payInt","acc01",["A1"]]
       ,["payPrin","acc01",["A1"]]
       ,["payPrin","acc01",["B"]]
       ,["payResidual","acc01","B"]]
    ,"CleanUp":[]
    ,"default":[]
    }


Action
  ``Action`` is a list, which annoates the action to be performed. In most of cases, the first element of list is the name of action, rest of elements are describing the fund movements(fund source and fund target)/ state change like update trigger status / fee accrual /bond interest accrual.

Fee 
^^^^^^

  * Calc Fee -> calculate the due balance of a fee
    
    * format ``["calcFee",<Fee1> , <Fee2> ... ]``
  
  * PayFee -> pay to a fee till due balance is 0

    syntax ``["payFee", {Account}, [<Fees>]]``

      *  ``{Account}`` -> Using the available funds from a single account.
      *  ``[<Fees>]`` -> Pay the fees in the list on pro-rata basis

    Using one more map to limit the amount to be paid

      * ``DuePct`` , limit the percentage of fee due to be paid
      * ``DueCapAmt`` ,  cap the paid amount to the fee
      ie. ``["payFee", "CashAccount", ["ServiceFee"], {"DuePct":0.1}]``

  * PayFeeResidual -> pay to a fee regardless the amount due
    
    * format ``["payFeeResidual", {Account}, {Fee} ]``
    * format ``["payFeeResidual", {Account}, {Fee}, <Limit> ]``

Bond
^^^^^^

  * Calc Bond Int -> calculate the due balance of a bond
    
    * format ``["calcBondInt", <Bond1> , <Bond2> ... ]``
 
  * PayInt -> pay interset to a bond till due int balance is 0

    * format ``["payInt", {Account}, [<Bonds>] ]``
  
  * AccrueAndPayInt -> accrue interest and pay interset to a bond till due int balance is 0

    * format ``["accrueAndPayInt", {Account}, [<Bonds>] ]``

  * PayPrin -> pay principal to a bond till due principal balance is 0

    * format ``["payPrin", {Account}, [<Bonds>] ]``
    * format ``["payPrin", {Account}, [<Bonds>], <Limit>]``

    the ``<Limit>`` is the magic key to make principal payment more versatile. User can control the amount to be paid via a :ref:`Formula` ie.
       *  (from deal: Autoflorence) the target amount is ` (end pool balance - (end pool balance * subordination percentage(12%)))`
          
          .. code-block:: python

            ["payPrin","SourceAccount","A"
                      ,{"formula": ("substract"
                                      ,("poolBalance",)
                                      ,("factor"
                                         ,("poolBalance",), 0.12))}]
  
  * PayPrinResidual -> pay principal to a bond regardless its due principal balance
    
    * format ``["payPrinResidual", {Account}, <Bond> ]``
  
  * PayResidual  -> pay interest to a bond regardless its interest due.
    
    * format ``["payResidual", {Account}, <Bond> ]``
    * format ``["payResidual", {Account}, <Bond>, <Limit> ]``
  
Account
^^^^^^^^^

  * Transfer -> transfer all the funds to the other account 
   
    * format ``["transfer", {Account}, {Account}]``
  
    transfer funds to the other account by <Limit>

    * format ``["transfer", {Account}, {Account}, <limit> ]``
    * format ``["transfer", {Account}, {Account}, {satisfy} ]``
      * satisfy = ``{"reserve":"gap"}`` -> transfer till reserve amount of *target* account is met
      * satisfy = ``{"reserve":"excess"}`` -> transfer till reserve amount of *source* account is met

Buy & Sell Assets 
^^^^^^^^^^^^^^^^^^^^^^^

  * Liquidation -> sell the assets and deposit the proceeds to the account
   
    * format ``["sellAsset", {pricing method}, {Account}]``
      
  * Buy Asset -> use cash from an account to buy assets.
  
    * format ``["buyAsset",{pricing method}, {Account}, {limit}]``

      * ``limit`` can be either a :ref:`Formula` or a Cap Amount
      

Liquidtiy Facility 
^^^^^^^^^^^^^^^^^^^

Liquidity Facility 
  it behaves like a 3rd party entity which support the cashflow distirbution in case of shortgage. It can depoit cash to account via ``liqSupport``, with optinal a ``limit``.
    
  * Liquidity Support -> deposit cash to account from a liquidity provider, subject to its available balance.
  
    * format ``["liqSupport", <liqProvider>,<Account>]``
  
  * Or, only deposit to account with shortage amount described by ``<Limit>`` ,which can be a ``formula``

    * format ``["liqSupport", <liqProvider>,"account",<Account Name>,<Limit>]``
    * format ``["liqSupport", <liqProvider>,"fee",<Fee Name>,<Limit>]``
    * format ``["liqSupport", <liqProvider>,"interest",<Bond Name>,<Limit>]``
    * format ``["liqSupport", <liqProvider>,"principal",<Bond Name>,<Limit>]``

  * Liquidity Repay & Compensation -> pay back to liquidity provider till its balance is 0

    * format ``["liqRepay","bal" , <Account>, <liqProvider>,<Limit>]``
    * format ``["liqRepay","int" , <Account>, <liqProvider>,<Limit>]``
    * format ``["liqRepay","premium" , <Account>, <liqProvider>,<Limit>]``
  
  * Or, pay all the residual cash back to the provider 
  
    * format ``["liqRepayResidual", <Account>, <liqProvider>]``



Conditional Action
^^^^^^^^^^^^^^^^^^^^

There are two types of `Conditional Action`, which are same in with "IF" / "IF-ELSE" clause in programming language

format : ``["If",<conditon>,<Action1>,<Action2>....]``

waterfall actions follows will be executed if certain `Condtion`_ is met.


format : ``["IfElse",<conditon>``
                    ``,[<Action1>,<Action2>....]``
                    ``,[<Action1>,<Action2>....]``
                    ``]``
                    
first list of actions will be executed if ``condtion`` was met , otherwise , second list of actions will be executed


Trigger
-----------

`Trigger` is a generalized concept in `absbox`/`Hastructure`, it is not limited to <pool performance> related design to protect tranches but a border concpet as below:

.. image:: img/trigger.png
  :width: 500
  :alt: version


There are 4 components in Triggers:

  * ``Condition`` -> it will fire the trigger effects, when :ref:`Condition` is met
  * ``Effects`` -> what would happen if the trigger is fired
  * ``Status`` -> it is triggered or not 
  * ``Curable`` -> whether the trigger is curable

When to run trigger
^^^^^^^^^^^^^^^^^^^^^^
  
  Trigger can run at 5 point of time.
  
  * Start/End of each Pool Collection Day -> ``BeforeCollect`` / ``AfterCollect``
  * Start/End of each Distribution Day    -> ``BeforeDistribution`` / ``AfterDistribution``
  * During any point of waterfall 


.. image:: img/trigger_in_deal_run.png
  :width: 600
  :alt: trigger_loc



Conditons of a trigger
^^^^^^^^^^^^^^^^^^^^^^^^^

Magically, condition of a trigger is just a :ref:`Condition` from the very begining ! We just reuse that component.


Effects/Consequence of a trigger
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  
Trigger will update the `state` of a deal, like:

  * convert `revolving` to `amortizing`
  * convert `amortizing` to `accelerated`
  * convert `amortizing` to `defaulted`

.. code-block:: python
  
  "effects":("newStatus","Amortizing") # change deal status to "Amortizing"
  "effects":("newStatus","Accelerated") # change deal status to "Accelerated"
  "effects":("newStatus","Defaulted") # change deal status to "Defautled"

Once the `state` of deal changed, the deal will pick the corresponding waterfall to run at distribution days.

  * accure some certain fee 

.. code-block:: python
  
  "effects":["accrueFees","feeName1","feeName2",...]

  * change reserve target balance of an account

.. code-block:: python
  
  "effects":["newReserveBalance","accName1",{"fixReserve":1000}]
  "effects":["newReserveBalance","accName1",{"targetReserve":["......"]}]

  * create a new trigger 

.. code-block:: python
  
  "effects":[("newTrigger"
              ,{"condition":...
               ,"effects":...
               ,"status":...
               ,"curable":...})]

  * a list of above

.. code-block:: python
  
  "effects":["Effects"
             ,<effect 1>
             ,<effect 2>
             ,....]


Examples  

.. code-block:: python

    {
      "BeforeCollect":[]
      ,"AfterCollect":[
        {"condition":[("cumPoolDefaultedRate",),">",0.05]
        ,"effects":("newStatus","Defaulted")
        ,"status":False
        ,"curable":False}
      ]
      ,"BeforeDistribution":[
        {"condition":[">=","2025-01-01"]
        ,"effects":("newStatus","Defaulted")
        ,"status":False
        ,"curable":False}
      ]
      ,"AfterDistribution":[
        {"condition":[("bondFactor",),"<=",0.1]
        ,"effects":("newStatus","Accelerated")
        ,"status":False
        ,"curable":False}
      ]
      }
    }

    #a list of triggers effects
    {
      "AfterCollect":[
        {"condition":[("cumPoolDefaultedRate",),">",0.05]
        ,"effects":("Effects"
                    ,("newStatus","Defaulted")
                    ,("accrueFees","feeA","feeB"))
        ,"status":False
        ,"curable":False}
      ]
    }

    # ALL and ANY logic of triggers ( and they can nested toghter ! )
    ,{"AfterCollect":[
        {"condition":["any"
                       ,[("cumPoolDefaultedRate",),">",0.05]
                       ,[">","2021-09-15"]]
        ,"effects":("newStatus","Accelerated")
        ,"status":False
        ,"curable":False}
        ]}

    ,{"AfterCollect":[
        {"condition":["all"
                      ,[("cumPoolDefaultedRate",),">",0.05]
                      ,[">","2021-09-15"]]
        ,"effects":("newStatus","Accelerated")
        ,"status":False
        ,"curable":False}
        ]}

Liquidity Provider
---------------------

`Liquidity Provider` is an external entity which can be used as a line of credit/insuer. If there is a shortage on fee or interest or principal, user can setup rules to draw cash from the `Likquidity Provider`  and deposity to accounts.


Interest Rate Swap
--------------------

`Interest Rate Swap` is a 3rd party entity ,which can either deposit money into a SPV or collecting money from SPV. The direction of cashflow depends on the strike rate vs interest rate curve in assumption.

it was modeled as a map ,with key as name to swap ,value serve as properties to swap. The very reason using a map becasue a deal can have multiple Swap contract.

properties:
* `settleDates` -> describe the setttlement dates .
* `pair` -> describe rates to swap (paying rate in left, receiving rate on right)
* `base` -> describe how reference balance is being updated 
* `start` -> when the swap contract come into effective
* `balance` -> (optional), current reference balance
* `lastSettleDate` -> (optional), last settle date which calculate `netcash`
* `netcash` -> (optional), current cash to pay/to collect 
* `stmt` -> (optional),transaction history

example: 

.. code-block:: python

  swap = {
      "swap1":{"settleDates":"MonthEnd"
               ,"pair":[("LPR5Y",0.01),0.05] # paying a float rate with spread ,and receiving a fix annualized rate
               ,"base":{"formula":("poolBalance",)}
               ,"start":"2021-06-25"
               ,"balance":2093.87}
  }


Examples
============

.. _exmaple-01:

Subordination
---------------

  * Subordination
  * One-off fees
  
.. literalinclude:: deal_sample/test01.py
   :language: python
   :emphasize-lines: 30,33-36

Multiple Waterfalls with triggers
------------------------------------

There can be multiple waterfalls which corresponding to `status`.
a acceleration/turbo event could be triggered and changing the payment sequence

* amortizing
* revolving
* accelerated
* defaulted 
* clean up 
  
.. literalinclude:: deal_sample/test02.py
   :language: python
   :emphasize-lines: 38-55


Define Conditional Action
------------------------------------

User can specify a condtional clause in the waterfall.

Only the conditions were met, actions following will be executed.

  
.. literalinclude:: deal_sample/test03.py
   :language: python
   :emphasize-lines: 42-44

Split income by percentage 
----------------------------

The deal docs may split income from pools by pct% to another account 

.. literalinclude:: deal_sample/test04.py
   :language: python
   :emphasize-lines: 39-40

Liquidation Provider /Insurance / Ganrantee
----------------------------------------------

Liquidation provider will deposit the gap amount of interest due against the account available balance.
And it will start to be repaid if both A1 and B tranche were paid off

Fixed amount with interest accured.

.. literalinclude:: deal_sample/test05.py
   :language: python
   :emphasize-lines: 34-38,44-45,52-54

Using a formula to cap the support amount.

.. literalinclude:: deal_sample/test06.py
   :language: python
   :emphasize-lines: 33-37,43-44,51-53

Step-Up coupon 
----------------------------------------------

User can model a step up bond which start to increase a spread after a certain day by an interval specified by <datepattern>

.. literalinclude:: deal_sample/stepup_sample.py
   :language: python
   :emphasize-lines: 20

BMW Auto Deal 2023-01
--------------------------

* Revolving structure with revolving asset perf assumption / pricing method 
* Formula based way to transfer cash between accounts
* Conditional action base on trigger 
* IF-ELSE clause in waterfall action
* Pay residual value to a fee
* Buy/Sell asset via a pricing method

.. literalinclude:: deal_sample/test07.py
   :language: python

Ginnie Mae /ARM Mortgage Deal 
------------------------------------
* Model an ARM 
* Using a rate curve
* Using variable fee rate ( a formula based `rate` for a formula)

.. literalinclude:: deal_sample/test08.py
   :language: python

Limit Principal Payment
------------------------------------

* Using a formula to limit the principal repayment of a bond 
* Using `Inspect` to view the formula value 


.. literalinclude:: deal_sample/test09.py
   :language: python
   :emphasize-lines: 3-5,42,58-59

Interest Rate Swap
-----------------------

* Setup a swap instrument ,merge it into a deal map
* using shortcut `mkDeal` to create a generic deal object 
* Swap can reference a notion with a `formula`

.. literalinclude:: deal_sample/test10.py
   :language: python


JSON
=========

A deal object can be converted into json format via a property field `.json`

.. code-block:: python
   
   #Assuming 

   test.json  

   #{'tag': 'MDeal',
   # 'contents': {'dates': {'tag': 'PreClosingDates',
   #   'contents': ['2021-03-01',
   #    '2021-06-15',
   #    None,
   #    '2030-01-01',
   #    ['2021-06-15', {'tag': 'MonthEnd'}],
   #    ['2021-07-26', {'tag': 'DayOfMonth', 'contents': 20}]]},
   #  'name': 'Multiple Waterfall',
   #  'status': {'tag': 'Amortizing'},
   #  'pool': {'assets': [{'tag': 'Mortgage',
   #     'contents': [{'originBalanc

 




