Modeling
****

.. autosummary::
   :toctree: generated

Deal modeling is a process to build a deal with descriptive factual data, like:

* Bond info
* Waterfall info
  * Describe the priority of payments allocation of
    * End of pool collection (Optional)
    * Distribution day for all the bonds and fees 
    * Event of Default (Optional)
    * Clean up call (Optional)
* Dates info
  * Cutoff day / Closing Date / Next/First payment Date
* Pools info
  * Either loan level data
  * Or forcased pool cashflow 
* Triggers (Optional)
* Liquidity Provider (Optional)

`absbox` ships with couple built-in class to accomodate serval deal typs, like Agency MBS or Automobile Loans Deal.

.. _Generic ABS:

Generic
====
.. code-block:: python

    from absbox import generic 


Components
=========
Dates
---------

- `Closing Date`: All pool cashflow after `Closing Date` belongs to the SPV

- `Settle Date`: Bond start to accure interest after `Settle Date`.w

- `First Pay Date` / `Next Pay Date`: First execution of waterfall or next date of executing the waterfall


.. code-block:: python

    {"cutoff":"2022-11-01"
    ,"closing":"2022-11-15"
    ,"nextPay":"2022-12-26"
    ,"stated":"2030-01-01"
    ,"poolFreq":"MonthEnd"
    ,"payFreq":["DayOfMonth",20]
    }

Date Pattern
^^^^^^^^^^

* "MonthEnd"
* "QuarterEnd"
* "YearEnd"
* "MonthFirst"
* "QuarterFirst"
* "YearFirst"
* ["MonthDayOfYear",M,D]
* ["DayOfMonth",M]

Formula 
---------
Structured product is using ``formula`` to restructure the cashflow distribution on the liabilities.
``absbox`` reuse the concept of ``formula`` in an extreamly powerful way, a ``formula`` can be

* Bond 
    * bondBalance -> sum of all bond balance
    * bondBalanceOf [String] -> sum of balance of specified bonds
    * originalBondBalance
    * bondFactor
* Pool 
    * poolBalance
    * originalPoolBalance
    * poolFactor
* Accounts
    * accountBalance -> sum of all account balance
    * accountBalance [String] -> sum of specified account balance
    * reserveGap [String] -> sum of shortfall of reserve amount of specified accounts
* Due Amount 
    * bondDueInt [String] -> sum of bond interest due
    * feeDue [String] -> sum of fee due
* Combination
    * factor <Formula> <Number> -> multiply a value to a formula
    * Max <Formula> <Formula> -> get the higher value
    * Min <Formula> <Formula> -> get the lower value 
    * sum [<Formula>] -> sum of formula value
    * substract [<Formula>] -> using 1st of element to substract rest in the list
    * constant <Number>  -> a constant value
    * custom <Name of user define data>


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
  * custom fee flow,
      * an user defined date expenses, the date and amount can be customized.
      * like 100 USD at 2022-1-20 and incur other 20 USD at 2024-3-2



.. code-block:: python
  
  (("servicer_fee",{"type":{"annualPctFee":["poolBalance",0.02]}})
   ,("bond_service_fee",{"type":{"pctFee":["bondBalance",0.02]}})
   ,("issuance_fee",{"type":{"fixFee":100}})
   ,("rating_fee",{"type":{"recurFee":[["MonthDayOfYear",6,30],15]}})
  )

Pool
---------

a ``Pool`` represents a set of assets ,which generate cashflows to support expenses and liabilities.

* it can either has a loan level ``asset`` or ``projected cashflow``
* other optional fields like `issuance balance`

Mortgage
^^^^^^^^
.. code-block:: python

  [["Mortgage"
        ,{"faceValue":120,"originRate":["Fix",0.045],"originTerm":30
          ,"frequency":"Monthly","originDate":"2021-02-01"}
          ,{"currentBalance":120
          ,"currentRate":0.08
          ,"remainTerms":20
          ,"status":"current"}]]

Accounts
---------

There are two types of accounts:

  * `Bank Account` -> which used to collect money from pool and pay out to fees/bonds
  * `Reserve Account` -> with one more attribute to `Bank Account` which specifies target reserve amount of the account

Format ``({account name},{account description})``, i.e

* Bank Account

.. code-block:: python

  (("principalAccount",{"balance":0})
   ,("repaymentAccount",{"balance":0}))

Reserve Account
^^^^^^^^^^^^^^

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

Interest/Investment 
^^^^^^^^^^^^^^^^^^^

model the interest or short-term investment income in the account.

syntax: 
``{"period": <date Pattern>,"rate": <number>,"lastSettleDate":<date>}``

.. code-block:: python

  ("ReserveAccountA",{"balance":0
                    ,"type":{"fixReserve":1000}
                    ,"interest":{"period":"QuarterEnd"
                                 ,"rate":0.05
                                 ,"lastSettleDate":"2022-11-02"}})


Bonds/Tranches
---------------

syntax ``({bond/tranche name},{bond/tranche description})`` ,

there are 2 types of `Interest`

  * Fix Rate   :code:`"rateType":{"fix":0.0569}`
  * Float Rate   :code:`"rateType":{"floater":["SOFAR1Y",-0.0169,"Monthly"]}`

there are 4 types of `Principal` for bonds/tranches

  * `Sequential`： can be paid down as much as its oustanding balance
  * `PAC`： Balance of bond can only be paid down by a predefined schedule
  * `Lockout`： Principal won't be paid after lockout date
  * `Equity`：  No interest and shall serve as junior tranche

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
----

Waterfall means a list of ``action`` involves cash movement.

`action`

  * PayFee

    syntax ``["payFee", [{Account}], [<Fees>]]``

      *  ``[{Account}]`` -> Using the available funds of accounts in the list from 1st ,then 2nd ..
      *  ``[<Fees>]`` -> Pay the fees in the list on pro-rata basis

  * PayFeeBy

    * Using one more map to limit the amount to be paid

      * ``DuePct`` , limit the percentage of fee due to be paid
      * ``DueCapAmt`` ,  cap the paid amount to the fee
      ie. ``["PayFeeBy", ["CashAccount"], ["ServiceFee"], {"DuePct":0.1}]``

  * PayFeeResidual
  
    * format ``["payFeeResidual", {Account}, {Fee} ]``
    * format ``["payFeeResidual", {Account}, {Fee}, <Limit> ]``

  * PayInt

    * format ``["payInt", {Account}, [<Bonds>] ]``

  * PayPrin

    * format ``["payPrin", {Account}, [<Bonds>] ]``
    * format ``["payPrinBy", {Account}, [<Bonds>], <Limit>]``
  
  * PayPrinResidual 
    
    * format ``["payPrinResidual", {Account}, <Bond> ]``
  
  * PayResidual 
    
    * format ``["payResidual", {Account}, <Bond> ]``
    * format ``["payResidual", {Account}, <Bond>, <Limit> ]``
  

  * Transfer
   
    * format ``["transfer", {Account}, {Account}]``
  
  * TransferBy
   
    * format ``["transferBy",<limit> , {Account}, {Account}]``
  
  * Calc Fee 
    
    * format ``["calcFee",<Fee1> , <Fee2> ... ]``
  
  * Calc Bond Int
    
    * format ``["calcBondInt", <Bond1> , <Bond2> ... ]``
  
  * TransferReserve
   
    * format ``["transferReserve", {Account}, {Account}, {satisfy} ]``
      * satisfy = "target" -> transfer till reserve amount of *target* account is met
      * satisfy = "source" -> transfer till reserve amount of *source* account is met

  * Liquidation
   
    * format ``["sellAsset", {LiquidationMethod}, {Account}]``
    
  * Liquidity Support
  
    * format ``["liqSupport", <liqProvider>,<Account>,<Limit>]``
    * format ``["liqSupport", <liqProvider>,<Account>]``
  
  * Liquidity Repay & Compensation
    * format ``["liqRepay", <Account>, <liqProvider>]``
    * format ``["liqRepayResidual", <Account>, <liqProvider>]``
  

`Waterfall`: there are 3 waterfalls in a deal 

  * ``Normal``, executing when deal is *not defaulted*
  * ``CollectionEnd``, executing at end of pool collection period
  * ``CleanUp``, executing when deal is being *clean up*


ie：

.. code-block:: python

   {"Normal":[
       ["PayFee",["acc01"],['trusteeFee']]
       ,["PayInt","acc01",["A1"]]
       ,["PayPrin","acc01",["A1"]]
       ,["PayPrin","acc01",["B"]]
       ,["PayEquityResidual","acc01","B"]]
    ,"CleanUp":[]
    ,"Defaulted":[]
    }


Examples
====

Subordination
----

  * Subordination
  * One-off fees
  
.. literalinclude:: deal_sample/test01.py
   :language: python



Save a deal file
====

Save
----
using ``save()`` to save a deal file to disk

.. code-block:: python

  ...
  from absbox import API,save
  deal = .... #
  save(deal,"path/to/file")

Load
----
 ``load()`` to load a deal from disk

.. code-block:: python

  ...
  from absbox.local.generic import Generic
  Generic.load("path/to/file")
