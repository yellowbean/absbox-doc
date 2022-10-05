Modeling
****

.. autosummary::
   :toctree: generated

Deal Modeling is a process to build a deal with descriptive factual data, like:

* Bond info
* Waterfall info
* Dates info
* Pools info

`absbox` ships with couple built-in class to accomodate serval deal typs, like Agency MBS or Automobile Loans Deal.

.. _Generic ABS:

Generic
====
.. code-block:: python

   from absbox import generic 


Components
====
Dates
----

- `Closing Date`: All pool cashflow after `Closing Date` will be flow into the SPV

- `Settle Date`: Bond start to accure interest after `Settle Date`

- `First Pay Date` / `Next Pay Date`: First execution of waterfall or next date of executing the waterfall


.. code-block:: python

  ("2022-01-01","2022-03-01","2022-05-01")
  # which means
  # closing date=2022-01-01
  # last paid date=2022-03-01
  # first pay date/next pay date=2022-05-01


.. code-block:: python

  ("2022-09-01","2022-09-26","2022-10-26")
  # 2022-09-01, all pool projected cashflow will be follow to SPV after this date
  # 2022-09-26，all the bonds start to accure interest after this date
  # 2022-10-26, next payment date

Fee/Expenses
----

Fees fall into couple categories:
  * one-off, with initial balance and won't get paid after initial balance was paid off。
  * recur fee , a fix amount fee which occur by an interval like `Monthly` or `Yearly`
  * pecerntage fee, a fee type which the due amount depends on a percentage of balance, ie
     * using ``current pool balance/current bond balance`` as base and multiply with an annualise percentage.

format： ``({fee name} , {fee description} )``

.. code-block:: python
  #two fees
  (("servicer_fee",{"type":{"AnnualPctFee":["PoolBalance",0.02]}})
   ,("bond_service_fee",{"type":{"PctFee":["BondBalance",0.02]}})
   ,("issuance_fee",{"type":{"FixFee":100}})
  )

Pool
----

Mortgage

.. code-block:: python

  [["Mortgage"
        ,{"faceValue":120,"originRate":["Fix",0.045],"originTerm":30
          ,"frequency":"Monthly","originDate":"2021-02-01"}
          ,{"currentBalance":120
          ,"currentRate":0.08
          ,"remainTerms":20
          ,"status":"current"}]]

Accounts
----
There are two types of accounts,
  * Bank Account -> which used to collect money from pool and pay out to fees/bonds
  * Reserve Account -> with one more attribute to `Bank Account` which set the reserve amount of the account

Format ``({account name},{account description})``, i.e

* Bank Account

.. code-block:: python

  (("principalAccount",{"balance":0})
   ,("repaymentAccount",{"balance":0}))

* Reserve Account 

There is one extra attribute to set : `type`

  * Fix Amount： a single reserve amount 
    ``("ReserveAccountA",{"balance":0,"type":{"FixReserve":1000}})``
  * Formula： the target reserve amount is derived from a formula, like 2% of pool balance
    ``("ReserveAccountB",{"balance":0,"type":{"Target":["PctReserve",0.015]}})``
  * Nested Formula, the target reserve amount is base on higher or lower of two formula 

    .. code-block:: python

      ("ReserveAccountC",{"balance":0,"type":{"Max":[
                                     {"Target":["PoolBalance",0.015]}
                                    ,{"FixReserve":100}]})
      ("ReserveAccountD",{"balance":0,"type":{"Min":[
                                     {"Target":["PoolBalance",0.015]}
                                    ,{"FixReserve":100}]})
      ("ReserveAccountE",{"balance":0,"type":{"Min":[{"Max":[
                                            {"Target":["PoolBalance",0.015]}
                                            ,{"FixReserve":100}]}
                                    ,{"FixReserve":150}]})
Bonds/Tranches
----

format ``({bond/tranche name},{bond/tranche description})`` ， 
there are 3 types of `Interest`

  * Fix Rate   :code:`"rateType":{"Fix":0.0569}`
  * Float Rate   :code:`"rateType":{"Floater":["SOFAR1Y",-0.0169,"Monthly"]}`
  * Interim Yield   :code:`"rateType":{"InterimYield":0.02}`

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
           ,"rateType":{"Floater":["LPR5Y",-0.0169,"Monthly"]}
           ,"bondType":{"Sequential":None} })
      ,("A2",{"balance":5_444_000_000
           ,"rate":0.03
           ,"originBalance":5_444_000_000
           ,"originRate":0.03
           ,"startDate":"2020-01-03"
           ,"rateType":{"Floater":["LPR5Y",-0.0091,"Monthly"]}
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

Waterfall means a list of `action`` involves cash movement.

`action`
  * PayFee

    * format ``["PayFee", [{Account}], [<Fees>]]``
      *  ``[{Account}]`` -> Using the available funds of accounts in the list from 1st ,then 2nd ..
      *  ``[<Fees>]`` -> Pay the fees in the list on pro-rata basis

  * PayFeeBy

    * Using one more map to limit the amount to be paid

      * ``DuePct`` , limit the percentage of fee due to be paid
      * ``DueCapAmt`` ,  cap the paid amount to the fee
      ie. ``["PayFeeBy", ["CashAccount"], ["ServiceFee"], {"DuePct":0.1}]``

  * PayInt

    * format ``["PayInt", {Account}, [<Bonds>] ]``

  * PayPrin

    * format ``["PayPrin", {Account}, [<Bonds>] ]``

  * Transfer
   
    * format ``["Transfer", {Account}, {Account}]``
  
  * TransferReserve
   
    * format ``["TransferReserve", {Account}, {Account}, {satisfy} ]``
      * satisfy = "target" -> transfer till reserve amount of *target* account is met
      * satisfy = "source" -> transfer till reserve amount of *source* account is met

  * Liquidation
   
    * format ``["LiquidatePool", {LiquidationMethod}, {Account}]``

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
