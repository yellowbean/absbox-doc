Modeling
****

.. autosummary::
   :toctree: generated

Deal modeling is a process to build a deal with descriptive factual data, like:

* Asset info 
  
  Describe the pool asset attributes
* Bond info
* Waterfall info
  
  Describe the priority of payments allocation of

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


.. _Generic ABS:

Generic
====
.. code-block:: python

    from absbox import generic 



DatePattern
--------

``<DatePattern>`` is used to decrible a series of dates .

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

Condition
----------

condition is a `boolean` type criteria ,

* it can be setup in reserve account to setup different target reserve amount;
* or in the waterfall to run the distribution action only when the critera is met;
  
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
----

Waterfall means a list of ``action`` involves cash movement.


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
^^^^^^^^^^^
    
  * Liquidity Support -> deposit cash to account from a liquidity provider, subject to its available balance.
  
    * format ``["liqSupport", <liqProvider>,<Account>,<Limit>]``
    * format ``["liqSupport", <liqProvider>,<Account>]``
  
  * Liquidity Repay & Compensation -> pay back to liquidity provider till its balance is 0 or regardless the balance.

    * format ``["liqRepay", <Account>, <liqProvider>]``
    * format ``["liqRepayResidual", <Account>, <liqProvider>]``
  
Conditional Action
^^^^^^^^^^^^^^^^

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
