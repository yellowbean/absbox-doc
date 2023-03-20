Modeling
***********

.. autosummary::
   :toctree: generated

Deal modeling is a process to build a deal with descriptive data, like:

* Asset info -> pool asset attributes, loan by loan or repline level data
* Bond info -> bonds with different types as well as residuel tranche
* Waterfall info -> Describe the priority of payments allocation of
    * End of pool collection (Optional)
    * Distribution day for all the bonds and fees 
    * Event of Default (Optional)
    * Clean up call (Optional)
* Dates info
  * Cutoff day / Closing Date / Next/First payment Date
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

`Generic` is a class that represent `SPV` which contains the dates/liabilities/assets/waterfall/trigger information.

.. code-block:: python
    
    from absbox.local.generic import Generic

DatePattern
-------------

``<DatePattern>`` is used to decrible a series of dates .

* "MonthEnd"  -> Month End ,like Jan 31, Feb 28/29 
* "QuarterEnd"  -> March 31, Jun 30, Sep 30, Dec 31
* "YearEnd" -> Dec 31
* "MonthFirst"  -> Jun 1, May 1
* "QuarterFirst" -> March 1 , Jun 1 , Sep 1 , Dec 1
* "YearFirst" -> Jan 1
* ["MonthDayOfYear",M,D] -> A day of the year, like Feb 14 on every year 
* ["DayOfMonth",M] -> A day of the month , like 15 on each month

Formula 
---------

Structured product is using ``formula`` to define the amount of account transfer, principal paydown or fee pay limit etc.

``absbox`` use the concept of ``formula`` in an extreamly composible way, a ``formula`` can be a variable reference to deal attributes.

* Bond 
    * bondBalance -> sum of all bond balance
    * bondBalanceOf [String] -> sum of balance of specified bonds
    * originalBondBalance -> bond balance at issuance
    * bondFactor
* Pool 
    * poolBalance  -> current pool balance
    * originalPoolBalance  -> pool original balance 
    * poolFactor
* Accounts
    * accountBalance -> sum of all account balance
    * accountBalance [String] -> sum of specified account balance
    * reserveGap [String] -> sum of shortfall of reserve amount of specified accounts
* Due Amount 
    * bondDueInt [String] -> sum of bond interest due
    * feeDue [String] -> sum of fee due

Or `formula` can be an arithmetic calculation on itselfies.

* Combination
    * factor <Formula> <Number> -> multiply <Number> to a formula
    * Max <Formula> <Formula> -> get the higher value
    * Min <Formula> <Formula> -> get the lower value 
    * sum [<Formula>] -> sum of formula value
    * substract [<Formula>] -> using 1st of element to substract rest in the list
    * constant <Number>  -> a constant value
    * custom <Name of user define data>

Condition
------------

condition is a `boolean` type test

* it can be set up in reserve account to define different target reserve amount;
* or in the waterfall to run the distribution action only when the testing is passing;
  
* [<formula>,">",val] -> true when <formula> greater than a value
* [<formula>,"<",val] -> true when <formula> less than a value
* [<formula>,">=",val] -> true when <formula> greater or equals to a value
* [<formula>,"<=",val] -> true when <formula> less or equals than a value
* [<formula>,"=",val] -> true when <formula> equals to a value
* ["all",<condition>,<condition>] -> true if all of <condition> is true
* ["any",<condition>,<condition>] -> true if any of <condition> is true
* ["<",date] -> before certain date
* [">",date] -> after certain date
* ["<=",date] -> On or beore certain date
* [">=",date] -> On or after certain Date

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

  * one-off
      * with a balance and will be paid off once it paid down to zero
  * recurrance fee
      * a fix amount fee which occurs by defined ``Date Pattern``
  * pecentage fee, a fee type which the due amount depends on a percentage of ``Formula``
      * like a fee is base on 
          * percentage of `pool balance`
          * a percentage of pool collection `interest`
          * a higher/lower amount of two `formula`
          * a sum of `formula` 
          * ...
  * annualized fee, 
      * similar to `percentage fee` but it will use an annualized rate to multiply the value of ``Formula``.
          * either reference to pool balance  or bond balance , etc....
  * custom fee flow,
      * an user defined date expenses, the date and amount can be customized.
      * like 100 USD at 2022-1-20 and incur other 20 USD at 2024-3-2
  * count type fee,
      * the fee due equals to a number multiply a unit fee. The number is a formula reference.


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

Format ``({account name},{account description})``, i.e

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

  * Formula： the target reserve amount is derived from a formula, like 2% of pool balance
  
    .. code-block:: python

      ("ReserveAccountB",{"balance":0
                         ,"type":{"targetReserve":[("poolBalance",),0.015]}})

  * Nested Formula, the target reserve amount is base on higher or lower of two formula 

  * Conditional amount, the target reserve amount depends on ``condition``:
    
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

syntax ``({bond/tranche name},{bond/tranche description})`` ,

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

PAC
^^^^^^^^^^^
A bond with target amortize balance, it will stop recieving principal once its balance hit the targeted balance 

Lockout
^^^^^^^^^^^
A bond with ``Lockout`` type is used to setup bond with only recieve principal after the `lockout date`

Equity
^^^^^^^^^^^

``Equity`` type is used to model junior or equity slice of liabilites of the SPV

.. code-block:: python

    ("A1",{"balance":3_650_000_000
           ,"rate":0.03
           ,"originBalance":3_650_000_000
           ,"originRate":0.03
           ,"startDate":"2020-01-03"
           ,"rateType":{"Floater":["SOFAR1Y",-0.0169,"Monthly"]}
           ,"bondType":{"Sequential":None} })
      ,("A2",{"balance":5_444_000_000
           ,"rate":0.03
           ,"originBalance":5_444_000_000
           ,"originRate":0.03
           ,"startDate":"2020-01-03"
           ,"rateType":{"Floater":["SOFAR1Y",-0.0091,"Monthly"]}
           ,"bondType":{"Sequential":None} })
      ,("R",{"balance":900_883_783.62
           ,"rate":0.0
           ,"originBalance":2_123_875_534.53
           ,"originRate":0.00
           ,"startDate":"2020-01-03"
           ,"rateType":{"InterimYield":0.02}  
           ,"bondType":{"Equity":None} })



Waterfall
-------------

Waterfall means a list of ``action`` to be executed at bond payment date.

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
^^^^^^^

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
    
  * Liquidity Support -> deposit cash to account from a liquidity provider, subject to its available balance.
  
    * format ``["liqSupport", <liqProvider>,<Account>,<Limit>]``
    * format ``["liqSupport", <liqProvider>,<Account>]``
  
  * Liquidity Repay & Compensation -> pay back to liquidity provider till its balance is 0 or regardless the balance.

    * format ``["liqRepay", <Account>, <liqProvider>]``
    * format ``["liqRepayResidual", <Account>, <liqProvider>]``
  
Conditional Action
^^^^^^^^^^^^^^^^^^^

format : ``[<conditon>,<Action1>,<Action2>....]``


waterfall action can be setup only triggered if certain conditon is met.


`Waterfall`: there are 3 waterfalls in a deal 

  * ``Normal``, executing when deal is *not defaulted*
  * ``CollectionEnd``, executing at end of pool collection period
  * ``CleanUp``, executing when deal is being *clean up*


ie：

.. code-block:: python

   {"Normal":[
       ["payFee",["acc01"],['trusteeFee']]
       ,["payInt","acc01",["A1"]]
       ,["payPrin","acc01",["A1"]]
       ,["payPrin","acc01",["B"]]
       ,["payResidual","acc01","B"]]
    ,"CleanUp":[]
    ,"Defaulted":[]
    }


Trigger(to be tested) 
^^^^^^^^^^^^^^^^^^^^^^^

* When to run trigger
  
  Trigger can run at 4 point of time.
  
  * Start/End of each Pool Collection Day
  * Start/End of each Distribution Day

* Conditon of a trigger
  
  trigger can be fired by comparing a `Formula` with :
  
  * greater/lower than a threshold/ value 
  * greater/lower than a threshold curve/ values associated with dates
  * AND/OR logic with other triggers

* Effect of a trigger
  
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

    "trigger":{
      "BeforeCollect":[]
      ,"AfterCollect":[
        ([("cumPoolDefaultedRate",),">",0.05]
          ,("newStatus","Defaulted"))
      ]
      ,"BeforeDistribution":[
        ([">=","2025-01-01"]
          ,("newStatus","Defaulted"))
      ]
      ,"AfterDistribution":[
        ([("bondFactor",),"<=",0.1]
         ,("newStatus","Accelerated"))
      ]
      }
    }

    #a list of triggers effects
    "trigger":{
      "AfterCollect":[
        ([("cumPoolDefaultedRate",),">",0.05]
          ,("Effects"
            ,("newStatus","Defaulted")
            ,("accrueFees","feeA","feeB")))
      ]
    }

    # ALL and ANY logic of triggers ( and they can nested toghter ! )
    "trigger":{
      "AfterCollect":[
        (["any"
           ,[("cumPoolDefaultedRate",),">",0.05]
           ,[("accountBalance","Acc01"),"<",5000]]
          ,("Effects"
            ,("newStatus","Defaulted")
            ,("accrueFees","feeA","feeB")))
      ]
    }



Examples
============

Subordination
---------------

  * Subordination
  * One-off fees
  
.. literalinclude:: deal_sample/test01.py
   :language: python

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



Save a deal file
===============

Save
-------------
using ``save()`` to save a deal file to disk

.. code-block:: python

  ...
  from absbox import API,save
  deal = .... #
  save(deal,"path/to/file")

Load
----------
 ``load()`` to load a deal from disk

.. code-block:: python

  ...
  from absbox.local.generic import Generic
  Generic.load("path/to/file")
