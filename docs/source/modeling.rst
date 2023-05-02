Modelling
***********

.. autosummary::
   :toctree: generated

Deal modeling is a process to build a deal with descriptive data, with components follows:

* Asset info -> pool asset attributes, loan by loan or repline level data or projected cashflow as input
* Bond info -> bonds with different types as well as residule tranche
* Waterfall info -> Describe the priority of payments when:
    * End of pool collection (Optional)
    * Distribution day for all the bonds and fees 
    * Event of Default (Optional)
    * Clean up call (Optional)
* Dates info
  * Cutoff day / Closing Date / Next/First payment Date or series of custom dates
* Triggers (Optional)
* Liquidity Provider (Optional)


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

Generic
===========

`Generic` is a class that represent `SPV` which contains the dates/liabilities/assets/waterfall/trigger/hedge information.

.. code-block:: python
    
    from absbox.local.generic import Generic


There are 4 reusable building blocks: ``<DatePattern>``, ``<Formula>``, ``<Condition>``, ``<Curve>``, all of them are being used in different components.


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
* ``["EveryNMonth","YYYY-MM-DD",N]`` -> a seriers day start with "YYYY-MM-DD", then every other N months afterwards
* ``["AllDatePattern",<datepattern1>,<datepattern2>.....]`` -> a union set of date pattern during the projection

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
* Pool 
    * ``("poolBalance",)``  -> current pool balance
    * ``("originalPoolBalance",)``  -> pool original balance 
    * ``("currentPoolDefaultedBalance",)``  -> pool defaulted balance 
    * ``("cumPoolDefaultedBalance",)``  -> pool cumulative defaulted balance 
    * ``("poolFactor",)`` -> pool factor
    * ``("borrowerNumber",)`` -> number of borrower
* Accounts
    * ``("accountBalance",)`` -> sum of all account balance
    * ``("accountBalance","A","B")`` -> sum of account balance for "A" and "B"
    * ``("reserveGap","A","B")`` -> sum of shortfall of reserve amount of specified accounts
* Expense
    * ``("feeDue","F1","F2")`` -> sum of fee due for fee "F1","F2"
    * ``("lastFeePaid","F1","F2")`` -> sum of fee last paid for fee "F1","F2"

Or `formula` can be an arithmetic calculation on itselfies.

* Combination
    * ``("factor", <Formula>,<Number>)`` -> multiply <Number> to a formula
    * ``("Max", <Formula>, <Formula>)`` -> get the higher value
    * ``("Min", <Formula>, <Formula>)`` -> get the lower value 
    * ``("sum", [<Formula>])`` -> sum of formula value
    * ``("substract", [<Formula>])`` -> using 1st of element to substract rest in the list
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
  * trigger status -> to be implement


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



Components
============

Dates
---------

Depends on the status of deal, the dates shall be modeled either in `ongoing` or `preclosing`

if it is `preclosing`

- `Cutoff Date`: All pool cashflow after `Closing Date` belongs to the SPV
- `Closing Date`:  after `Closing Date` belongs to the SPV
- `Settle Date`: Bond start to accrue interest after `Settle Date`.
- `First Pay Date`: First execution of payment waterfall
- `stated` : legal maturity date of the deal.
- `poolFeq` : describle the dates that collect cashflow from pool
- `payFeq` : describle the dates that distribution funds to fees and bonds.

.. code-block:: python

    {"cutoff":"2022-11-01"
    ,"closing":"2022-11-15"
    ,"firstPay":"2022-12-26"
    ,"stated":"2030-01-01"
    ,"poolFreq":"MonthEnd"
    ,"payFreq":["DayOfMonth",20]
    }


if deal is `ongoing`, the difference is that in `preclosing` mode, the projection will include an event of `OnClosingDate` which describe a sequence of actions to be performed at the date of `closing`


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

syntax: ``({fee name} , {fee description} )``, fees fall into types:

one-off fee
^^^^^^^^^^^^^^^^^^

with a balance and will be paid off once it paid down to zero

recurrance fee
^^^^^^^^^^^^^^^^

a fix amount fee which occurs by defined ``Date Pattern``


percentage fee
^^^^^^^^^^^^^^^^^^^
pecentage fee, a fee type which the due amount depends on a percentage of ``Formula``

like a fee is base on 

  * percentage of `pool balance`
  * a percentage of pool collection `interest`
  * a higher/lower amount of two `formula`
  * a sum of `formula` 
  * ...

annualized fee
^^^^^^^^^^^^^^^^

similar to `percentage fee` but it will use an annualized rate to multiply the value of ``Formula``.
either reference to pool balance  or bond balance , etc....


custom fee flow
^^^^^^^^^^^^^^^^^^^

an user defined date expenses, the date and amount can be customized.

like 100 USD at 2022-1-20 and incur other 20 USD at 2024-3-2


count type fee
^^^^^^^^^^^^^^^^^^^

the fee due equals to a number multiply a unit fee. The number is a formula reference.


.. code-block:: python
  
  (("servicer_fee",{"type":{"annualPctFee":["poolBalance",0.02]}})
   ,("bond_service_fee",{"type":{"pctFee":["bondBalance",0.02]}})
   ,("issuance_fee",{"type":{"fixFee":100}})
   ,("rating_fee",{"type":{"recurFee":[["MonthDayOfYear",6,30],15]}})
   ,("borrowerFee",{"type":{"numFee":[["DayOfMonth",20],("borrowerNumber",),1]}}
  )


Pool
---------

``Pool`` represents a set of assets ,which generate cashflows to support expenses and liabilities.

* it can either has a loan level ``asset`` or ``projected cashflow``
* other optional fields like `issuance balance`

Mortgage
^^^^^^^^^^^

`Mortgage` is a loan with level pay at each payment period.

`type` field can be used to define either its `Annuity` type or `Linear` Type

* `Level` -> `Annuity`
* `Even` -> `Linear`


.. code-block:: python


  ["Mortgage"
    ,{"originBalance": 12000.0
      ,"originRate": ["Fixed",0.045]
      ,"originTerm": 120
      ,"freq": "Monthly"
      ,"type": "Level"
      ,"originDate": "2021-02-01"}
    ,{"currentBalance": 10000.0
      ,"currentRate": 0.075
      ,"remainTerm": 80
      ,"status": "Current"}]

Loan
^^^^^^^^^^
`Loan` is type of asset which has interest only and a lump sum principal payment at end


.. code-block:: python


  ["Loan"
    ,{"originBalance": 80000
      ,"originRate": ["floater",0.045,{"index":"SOFR3M"
                                      ,"spread":0.01
                                      ,"reset":"Quarterly"}]
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
      ,"remainTerm",10}]


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

  * Formula： the target reserve amount is derived from a `Formula`_ , like 2% of pool balance
  
    .. code-block:: python

      ("ReserveAccountB",{"balance":0
                         ,"type":{"targetReserve":[("poolBalance",),0.015]}})

  * Nested Formula, the target reserve amount is base on higher or lower of two formula 

  * Conditional amount starts with ``"When"``, the target reserve amount depends on `Condition`_:
    
    * certain <formula> value is above or below certain value
    * satisfy all of ``condition`` s 
    * satisfy any one of ``condition`` s 
  
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

there are 2 types of `Interest`

  * Fix Rate   :code:`"rateType":{"fix":0.0569}`
  * Float Rate   :code:`"rateType":{"floater":["SOFR1Y",-0.0169,"Monthly"]}`

there are 4 types of `Principal` for bonds/tranches

  * `Sequential`： can be paid down as much as its oustanding balance
  * `PAC`： Balance of bond can only be paid down by a predefined schedule
  * `Lockout`： Principal won't be paid after lockout date
  * `Equity`：  No interest and shall serve as junior tranche

Sequential 
^^^^^^^^^^^
A bond with will receive principal till it's balance reduce to 0.

.. code-block:: python

    ("A1",{"balance":3_650_000_000
           ,"rate":0.03
           ,"originBalance":3_650_000_000
           ,"originRate":0.03
           ,"startDate":"2020-01-03"
           ,"rateType":{"Floater":["SOFAR1Y",-0.0169,"Monthly"]}
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

Waterfall means a list of ``action`` to be executed at bond payment day or pool collection day.

Fee 
^^^^^^

  * Calc Fee -> calculate the due balance of a fee
    
    * format ``["calcFee",<Fee1> , <Fee2> ... ]``
  
  * PayFee -> pay to a fee till due balance is 0

    syntax ``["payFee", [{Account}], [<Fees>]]``

      *  ``[{Account}]`` -> Using the available funds of accounts in the list from 1st ,then 2nd ..
      *  ``[<Fees>]`` -> Pay the fees in the list on pro-rata basis

  * PayFeeBy

    * Using one more map to limit the amount to be paid

      * ``DuePct`` , limit the percentage of fee due to be paid
      * ``DueCapAmt`` ,  cap the paid amount to the fee
      ie. ``["PayFeeBy", ["CashAccount"], ["ServiceFee"], {"DuePct":0.1}]``

  * PayFeeResidual -> pay to a fee regardless the amount due
    
    * format ``["payFeeResidual", {Account}, {Fee} ]``
    * format ``["payFeeResidual", {Account}, {Fee}, <Limit> ]``

Bond
^^^^^^

  * Calc Bond Int -> calculate the due balance of a bond
    
    * format ``["calcBondInt", <Bond1> , <Bond2> ... ]``
 
  * PayInt -> pay interset to a bond till due int balance is 0

    * format ``["payInt", {Account}, [<Bonds>] ]``

  * PayPrin -> pay principal to a bond till due principal balance is 0

    * format ``["payPrin", {Account}, [<Bonds>] ]``
    * format ``["payPrinBy", {Account}, [<Bonds>], <Limit>]``
  
  * PayPrinResidual -> pay principal to a bond regardless its due principal balance
    
    * format ``["payPrinResidual", {Account}, <Bond> ]``
  
  * PayResidual  -> pay interest to a bond regardless its interest due.
    
    * format ``["payResidual", {Account}, <Bond> ]``
    * format ``["payResidual", {Account}, <Bond>, <Limit> ]``
  
Account
^^^^^^^^^

  * Transfer -> transfer all the funds to the other account 
   
    * format ``["transfer", {Account}, {Account}]``
  
  * TransferBy -> transfer funds to the other account by <Limit>
   
    * format ``["transferBy", <limit> , {Account}, {Account}]``
  
 
  * TransferReserve -> transfer funds to other account till either one of reserve account met the target amount.
   
    * format ``["transferReserve", {Account}, {Account}, {satisfy} ]``

      * satisfy = "target" -> transfer till reserve amount of *target* account is met
      * satisfy = "source" -> transfer till reserve amount of *source* account is met

Call
^^^^^^

  * Liquidation -> sell the assets and deposit the proceeds to the account
   
    * format ``["sellAsset", {LiquidationMethod}, {Account}]``
      
Liquidtiy Facility 
^^^^^^^^^^^^^^^^^^^

Liquidity Facility 
  it behaves like a 3rd party entity which support the cashflow distirbution in case of shortgage. It can depoit cash to account via ``liqSupport``, with optinal a ``limit``.
    
  * Liquidity Support -> deposit cash to account from a liquidity provider, subject to its available balance.
  
    * format ``["liqSupport", <liqProvider>,<Account>]``
  
  * Or, only deposit to account with shortage amount described by ``<Limit>`` ,which can be a ``formula``

    * format ``["liqSupport", <liqProvider>,<Account>,<Limit>]``

  * Liquidity Repay & Compensation -> pay back to liquidity provider till its balance is 0

    * format ``["liqRepay", <Account>, <liqProvider>]``
  
  * Or, pay all the residual cash back to the provider 
  
    * format ``["liqRepayResidual", <Account>, <liqProvider>]``
  
Conditional Action
^^^^^^^^^^^^^^^^^^^^

format : ``["If",<conditon>,<Action1>,<Action2>....]``


waterfall action can be setup only triggered if certain `Condtion`_ is met.


`Waterfall`: there are couple waterfalls in a deal 

  * ``"amortizing"``, executing when deal is *not defaulted*
  * ``("amortizing","accelerated")``, executing when deal is *accelerated*
  * ``("amortizing","defaulted")``, executing when deal is *defaulted*
  * ``EndOfPoolCollection``, executing at end of pool collection period
  * ``closingDay``, executing only when the deal reach to closing day
  * ``CleanUp``, executing when deal is being *clean up*

ie：

.. code-block:: python

   {"amortizing":[
       ["payFee",["acc01"],['trusteeFee']]
       ,["payInt","acc01",["A1"]]
       ,["payPrin","acc01",["A1"]]
       ,["payPrin","acc01",["B"]]
       ,["payResidual","acc01","B"]]
    ,"CleanUp":[]
    ,"Defaulted":[]
    }


Trigger
-----------

There are 3 components in Triggers:

  * <Condition> -> it will fire the trigger effects, when <conditions> are met
  * <Effects> -> what would happen if the trigger is fired
  * <Status> -> it is triggered or not 
  * <Curable> -> whether the trigger is curable

When to run trigger
^^^^^^^^^^^^^^^^^^^^^^
  
  Trigger can run at 4 point of time.
  
  * Start/End of each Pool Collection Day -> ``BeforeCollect`` / ``AfterCollect``
  * Start/End of each Distribution Day    -> ``BeforeDistribution`` / ``AfterDistribution``

Conditons of a trigger
^^^^^^^^^^^^^^^^^^^^^^^^^

Magically, it just a `Condition`_ from the very begining ! We just reuse that component.


Effects/Consequence of a trigger
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  
  Trigger will update the `state` of a deal, like:

  * convert `revolving` to `amortizing`
  * convert `amortizing` to `accelerated`
  * convert `amortizing` to `defaulted`
  * or between any `state` , once the `state` of deal changed, the deal will pick the corresponding waterfall to run at distribution days.
  * accure some certain fee 
  * create a new trigger 
  * a list of above


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
   :emphasize-lines: 14,32

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



Save a deal file
===================

Binary
-------------

Save
^^^^^^^

using ``save()`` to save a deal file to disk

.. code-block:: python

  ...
  from absbox import API,save
  deal = .... #
  save(deal,"path/to/file")

Load
^^^^^^^^

``load()`` to load a deal from disk

.. code-block:: python

  ...
  from absbox.local.generic import Generic
  Generic.load("path/to/file")


JSON
----------

A deal object can be converted into json format via a properity field `.json`

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

 




