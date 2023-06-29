How To
========

a list of articles to show the power of ``absbox`` in Python world

How to load loan level data(Freddie Mac)
-------------------------------------------
it is quite common to load loan level data to the model:

* in structuring stage, loading different set of assets to the model to see if current captial structure is sound enough to pay off all the liabilities.
* in surveiliance stage, loading latest loan tape, then project the cashflow with updated assumptions as well to see how bond cashflow is changing in the future.

Since ``absbox`` model deal in plain python data structure => `list` and `map`, the process is quite straight-foward:

1. load data into Python data structure from IO (local desk file,)
2. map fields to asset structure in ``absbox``

here is an example from loan level data from .. _3132H3EE9: https://freddiemac.mbs-securities.com/freddie/details/3132H3EE9 (Freddie Mac)

Loading data
^^^^^^^^^^^^^^^

Freddie Mac disclose its loan level data in form of tabular data in text file.The hardway is using built-in funciton `open` to read each rows, the easy way will be load it via `pandas`.

Sample file :download:`3132H3EE9 <files/U90133_3132H3EE9_COLLAT_CURRENT.txt>`

.. code-block:: python

  import pandas as pd

  loan_tape = pd.read_csv("~/Downloads/U90133_3132H3EE9_COLLAT_CURRENT.txt",sep="|",dtype={'First Payment Date':str})


Here is couple fields we are interested in :

.. code-block:: python
 
  ["Mortgage"
    ,{"originBalance":2200,"originRate":["fix",0.045],"originTerm":30
     ,"freq":"Monthly","type":"Level","originDate":"2021-02-01"}
     ,{"currentBalance":2200
      ,"currentRate":0.08
      ,"remainTerm":20
     ,"status":"current"}]

The plain `mortgage` asset has two parts: (1) Origin information (2) Current Status, each of them were represented in form of a dict.

we can extract the corresponding fields from the loan tape.

.. warning::
    This mapping table only demostrate the how mapping works but not indicate the correct mapping!

.. list-table:: Map source fields
   :header-rows: 1

   * - source fields
     - absbox fields
     - notes
   * - "Mortgage Loan Amount"
     - originBalance
     -
   * - "Original Interest Rate"
     - originRate
     -
   * - "LoanTerm"
     - originTerm
     -
   * -
     - freq
     - hard code to "Monthly"
   * - "Amortization Type"
     - type
     - hard code to "Fix"
   * - "First Payment Date"
     - originDate 
     - Need to push "First Payment Date" back by a month
   * - "Current Investor Loan UPB"
     - currentBalance 
     -
   * - "Current Interest Rate"
     - currentRate 
     -
   * - "Remaining Months to Maturity"
     - remainTerm
     -
   * - "Days Delinquent"
     - status 
     -

Now we have the fields required, let's subset the dataframe with :

.. code-block:: python

    d = loan_tape[['Mortgage Loan Amount','Current Investor Loan UPB','Amortization Type','Original Interest Rate','First Payment Date'
                ,'Loan Term','Remaining Months to Maturity','Index','Current Interest Rate','Days Delinquent']]


Mapping fields
^^^^^^^^^^^^^^^

Source data may not be consist with format required, we need preprocessing the data if necessary:

.. code-block:: python

  mapped_df = pd.DataFrame()
  mapped_df['originBalance'] = d['Mortgage Loan Amount']
  mapped_df['originRate'] = [["fix",_/100] for _ in d['Original Interest Rate'].to_list() ]
  mapped_df['originTerm'] = d['Loan Term']
  mapped_df['freq'] = "Monthly" 
  mapped_df['type'] = "Level"
  mapped_df['originDate'] = (pd.to_datetime(d['First Payment Date']) - pd.DateOffset(months=1)).map(lambda x: x.strftime("%Y-%m-%d"))
  mapped_df['currentBalance'] = d['Current Investor Loan UPB']
  mapped_df['currentRate'] = d['Current Interest Rate']/100
  mapped_df['remainTerm'] = d['Remaining Months to Maturity']
  mapped_df['status'] =  d['Days Delinquent'].map(lambda x: "Current" if x=='Current' else "Defaulted")

Once we have the mapping table ready, the next step will be building a mapping function to convert loan tape data into `absbox` compliant style.

.. code-block:: python

  origin_fields = set(['originBalance', 'originRate', 'originTerm', 'freq', 'type', 'originDate'])
  current_fields = set(['currentBalance', 'currentRate', 'remainTerm', 'status'])
  
  mortgages = [["Mortgage"
                ,{k:v for k,v in x.items() if k in origin_fields}
                ,{k:v for k,v in x.items() if k in current_fields}]
                   for x in mapped_df.to_dict(orient="records")]

Happy running
^^^^^^^^^^^^^^^

Once we have built the loan level data `loans` , we can just plug it into the _dummy_ deal:

.. code-block:: python

  ### <<Dummy Deal>>
  loan_level_deal = Generic(
      "loan_level_deal"
      ,{"cutoff":"2023-03-01","closing":"2023-02-15","firstPay":"2023-04-20"
       ,"payFreq":["DayOfMonth",20],"poolFreq":"MonthEnd","stated":"2042-01-01"}
      ,{'assets':mortgages}  #<<<<<--- here
      ,(("acc01",{"balance":0}),)
      ,(("A1",{"balance":37498392.54
               ,"rate":0.03
               ,"originBalance":1000
               ,"originRate":0.07
               ,"startDate":"2020-01-03"
               ,"rateType":{"Fixed":0.08}
               ,"bondType":{"Sequential":None}}),)
      ,(("trusteeFee",{"type":{"fixFee":30}}),)
      ,{"amortizing":[
           ["payFee",["acc01"],['trusteeFee']]
           ,["payInt","acc01",["A1"]]
           ,["payPrin","acc01",["A1"]]
       ]}
      ,[["CollectedInterest","acc01"]
        ,["CollectedPrincipal","acc01"]
        ,["CollectedPrepayment","acc01"]
        ,["CollectedRecoveries","acc01"]]
      ,None
      ,None)

Then, project the cashflow with:

.. code-block:: python

  r = localAPI.run(loan_level_deal ,assumptions=[] ,read=True)

  r['pool']['flow'] # Now you shall able to view the loan level cashflow ! 

.. warning::
  if the `run()` call was slow, probably it is caused by network IO or CPU on the server, pls consider using a local docker image instead.

Conclusion
^^^^^^^^^^^^^^

There are numerious format carrying loan level data, it is recommended to wrap the your own function to accomodate.

in this case, we just need one funciton:

.. code-block:: python

  def read_freddie_mac(file_path:str):
      loan_tape = pd.read_csv(file_path,sep="|",dtype={'First Payment Date':str})
      d = loan_tape[['Mortgage Loan Amount','Current Investor Loan UPB','Amortization Type','Original Interest Rate','First Payment Date'
            ,'Loan Term','Remaining Months to Maturity','Index','Current Interest Rate','Days Delinquent']]

      mapped_df = pd.DataFrame()
      mapped_df['originBalance'] = d['Mortgage Loan Amount']
      mapped_df['originRate'] = [["fix",_/100] for _ in d['Original Interest Rate'].to_list() ]
      mapped_df['originTerm'] = d['Loan Term']
      mapped_df['freq'] = "Monthly"
      mapped_df['type'] = "Level"
      mapped_df['originDate'] = (pd.to_datetime(d['First Payment Date']) - pd.DateOffset(months=1)).map(lambda x: x.strftime("%Y-%m-%d"))
      mapped_df['currentBalance'] = d['Current Investor Loan UPB']
      mapped_df['currentRate'] = d['Current Interest Rate']/100
      mapped_df['remainTerm'] = d['Remaining Months to Maturity']
      mapped_df['status'] =  d['Days Delinquent'].map(lambda x: "Current" if x=='Current' else "Defaulted")

      origin_fields = set(['originBalance', 'originRate', 'originTerm', 'freq', 'type', 'originDate'])
      current_fields = set(['currentBalance', 'currentRate', 'remainTerm', 'status'])
      
      mortgages = [["Mortgage"
                    ,{k:v for k,v in x.items() if k in origin_fields}
                    ,{k:v for k,v in x.items() if k in current_fields}]
                      for x in mapped_df.to_dict(orient="records")]

      return mortgages


How to structuring a deal
-------------------------------------------

Structuring
  `Structuring` may have different meanings for different people, in this context, `structuring` means using different deal components to see what is most desired reuslt (like bond price, WAL ,duration, credit event ) for issuance purpose
  `Modelling` / `Reverse Engineering` means using data(bond,trigger,repline pool,waterfall) from offering memorandum to build a deal, the goal is to get best possible bond cashflow/pool cashflow for trading purpose

Strucuring a deal may looks intimidating, while the process is simple:

1. Given a base deal, create a bunch of new components 
2. Swap them into the deal, build the multiple deals
3. Compare the new result of interest,back to Step 2 if result is not desired.

Build components
^^^^^^^^^^^^^^^^^^

Assume we have already a base line model called :ref:`subordination exmaple <exmaple-01>` , now we want to see how differnt issuance size and issuance rate of the bonds would affect the pricing/bond cashflow.
(rationale : the smaller issuance size would require lower interest rate as short WAL)

.. code-block:: python

   # if senior balance = 1100, then rate is 7%
   # if senior balance = 1500, then rate is 8%
   issuance_plan = [ (1100,0.07),(1500,0.08) ]
   total_issuance_bal = 2000

   bond_plan = [ {"bonds":(("A1",{"balance":senior_bal
                             ,"rate":senior_r
                             ,"originBalance":senior_bal
                             ,"originRate":0.07
                             ,"startDate":"2020-01-03"
                             ,"rateType":{"Fixed":0.08}
                             ,"bondType":{"Sequential":None}})
                      ,("B",{"balance":(total_issuance_bal - senior_bal)
                             ,"rate":0.0
                             ,"originBalance":(total_issuance_bal - senior_bal)
                             ,"originRate":0.07
                             ,"startDate":"2020-01-03"
                             ,"rateType":{"Fixed":0.00}
                             ,"bondType":{"Equity":None}
                             }))}
        for senior_bal,senior_r in issuance_plan ]

Now we have ``bond_plan`` which has two bonds components, represents two different liability sizing structure.
(Same method applies to swapping different ``pool`` as well, user can swap different pool plans to structuring deals)



Build multiple deals
^^^^^^^^^^^^^^^^^^^^^^^

1. Now we need to build a dict with named key.
2. Call ``mkDealsBy`` ,which takes a base deal, and a dict which will be swaped into the base deal. It will return a map with same key of `bond_plan`, with new deals as value.
3. User can inspect ``differentDeals`` the reuslt via key.

.. code-block:: python

  bond_plan_with_name = dict(zip(["SmallSenior","HighSenior"],bond_plan))

  from absbox.local.util import mkDealsBy

  differentDeals = mkDealsBy(test01,bond_plan_with_name)
  
  differentDeals['HighSenior']


Set Assumption & Get Result 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run mulitple deal with same assumptions ,use ``runStructs()``

.. code-block:: python

  from absbox import API
  localAPI = API("https://absbox.org/api/latest")

  r = localAPI.runStructs(differentDeals
                          ,read=True
                          ,pricing= {"PVDate":"2021-08-22"
                                    ,"PVCurve":[["2021-01-01",0.025]
                                              ,["2024-08-01",0.025]]}
                          ,assumptions=[{"CPR":[0.02,0.02,0.03]}
                                      ,{"CDR":[0.01,0.015,0.021]}
                                      ,{"Recovery":(0.7,18)}]
                          )

Now the ``r`` is a map with key of "SmallSenior" and "HighSenior", value as cashflow of bond/pool/account/fee and a pricing.

.. image:: img/multi-pricing.png
  :width: 500
  :alt: pricing result 


.. code-block:: python

  #get A1 cashflow of each structure
  r['HighSenior']['bonds']['A1']
  r['SmallSenior']['bonds']['A1']

Whooray !


How to run a yield table
----------------------------

Prerequisite
^^^^^^^^^^^^^

* need a deal modeled
* pool performance assumption in a dict
* pricing assumption 

.. code-block:: python
   
  # pool performance  
  pool_assumps = {
       "CPR15":[{"CPR":0.15}]
      ,"CPR20":[{"CPR":0.20}]
      ,"CPR25":[{"CPR":0.25}]
  }
  # pricing curves and PV date
  pricing_assumps = {"PVDate":"2021-08-22"
                    ,"PVCurve":[["2021-01-01",0.025]
                               ,["2024-08-01",0.025]]}
  

Run with candy function
^^^^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: python

  # impor the candy function
  from absbox.local.analytics import run_yield_table

  from absbox import API
  localAPI = API("https://absbox.org/api/latest")


  # test01 is a deal object
  run_yield_table(localAPI, test01, "A1", pool_assumps, pricing_assumps )


.. image:: img/yield_table.png
  :width: 500
  :alt: yield_table

You have it !


How to model cashflow for ARM Mortgage 
---------------------------------------------

``absbox`` support ``ARM`` mortgage in verison ``0.15``

with features like:

* initPeriod (required) -> using fix rate in first N periods 
* initial reset cap (optional) -> maxium spread can be jump at first reset date.
* periodic reset cap (optional)-> maxium spread can be jump at rest reset dates.
* life cap (optional) -> maxium rate during the whole mortgage life cycle
* life floor (optional) -> minium rate during the whole mortgage life cycle


.. literalinclude:: deal_sample/arm_sample.py
   :language: python
   :emphasize-lines: 6,8-12,15


How to view projected quasi Financial Reports ?
-----------------------------------------------------

After the deal was run, user can view the cashflow of `pool`/ `bonds` `fees` etc  or transaction logs from `accounts`

.. code-block:: python

    r = localAPI.run(test01,
                     assumptions=[{"CDR":0.01},{"Recovery":(0.5,4)}],
                     read=True)

    #view result of bonds
    r['bonds']

    #transaction logs of accounts
    r['accounts']

    #pool cashflow 
    r['pool']['flow']

    #expenses
    r['fee']

For the users who is not patient enough or who want to take a high level view of how the deal was changing during the future.
`absbox` support `Financial Reports` since version `0.17.0`.

Syntax
^^^^^^^^^^

To query the `financial reports` , user need to add a dict in the list of `assumptions`.

.. code:: python 
   
    {"FinancialReports":{"dates":<DatePattern>}

the `<DatePattern>` will be used to describe `Financial Report Date`.

Example:

.. code-block:: python 

    r = localAPI.run(test01,
                     assumptions=[{"FinancialReports":{"dates":"MonthEnd"}}
                        ,{"CDR":0.01}
                        ,{"Recovery":(0.5,4)}],
                     read=True)

Cash Report 
^^^^^^^^^^^^

Cash Report will list a cash inflows and outflows of the deal. Report was compiled against transaction logs of `accounts`.


.. code-block:: python 

    r['result']['report']['cash']

.. image:: img/cash_report.png
  :width: 500
  :alt: cash_report




Balancesheet Report
^^^^^^^^^^^^^^^^^^^^

Balancesheet Report will take a `snapshot` of the deal on the dates describled in `DatePattern`.
It will also include the bond interest accured or fee accured as both of them are `Payable` in the balance sheet .

.. code-block:: python 

    r['result']['report']['balanceSheet']

.. image:: img/balance.png
  :width: 500
  :alt: balance


Model a revolving deal (BMW Auto)
-----------------------------------

Modelling a revolving deal is quite chanllenge , here is an real transaction which highlights the key components 

The whole model can be referred to here :ref:`BMW Auto Deal 2023-01`

Revolving Period
^^^^^^^^^^^^^^^^^^^
The revolving period usually was set like first 12/24 months after closing of deal. While the transaction may impose some other condition to enter `Amortization` stage when certain criteria was met, like pool cumulative default rate.

In this case, we model such event of `entering amortizating` with a trigger : 

  * if deal date was later than `2024-05-26` OR 
  * pool cumulative defaulted rate greater than 1.6%, 
  
then change the deal status from `Revolving` to `Amortizing`

.. code-block:: python 

  # a trigger 
  {"condition":["any"
                 ,[">=","2024-05-26"]
                 ,[("cumPoolDefaultedRate",),">",0.016]]
   ,"effects":("newStatus","Amortizing")
   ,"status":False
   ,"curable":False}

Once the deal enter a new status `Amortizing`, then in the waterfall acitons would branch base deal status :

.. code-block:: python 

  ["IfElse"  
    ,["status","Revolving"] # the predicate
    ,[["transferBy",{"formula":("substract",("bondBalance",),("poolBalance",))} # list of actions if predicate is True ()
                   ,"distAcc",'revolBuyAcc']
     ,["buyAsset",["Current|Defaulted",1.0,0],"revolBuyAcc",None]
     ,["payResidual","distAcc","Sub"] ]
    ,[["payPrin","distAcc",["A"]] # >>>> list of actions if deal is NOT  Revolving Status
     ,["payPrin","distAcc",["Sub"]]
     ,["payFeeResidual", "distAcc", "bmwFee"]]]]


Revolving Asset 
^^^^^^^^^^^^^^^^^^

Asset to be bought in the future isn't really part of deal data, thus we are going to supply these `dummy` asset in the `Assumption` 

Pls noted:

* revolving assets to be bought can be a `portfolio` which means a `list` of assets .
* user can set up a snapshot curve to simulate different assets at points of time in the future to be bought.
* user can set different pool performance assumption on the revolving pool 

.. code-block:: python 

  revol_asset = ["Mortgage"
                  ,{"originBalance":220,"originRate":["fix",0.043],"originTerm":48
                    ,"freq":"Monthly","type":"Level","originDate":"2021-07-01"}
                    ,{"currentBalance":220
                    ,"currentRate":0.043
                    ,"remainTerm":36
                    ,"status":"current"}]
  
  r = localAPI.run(BMW202301,
             assumptions=[{"RevolvingAssets":[["constant",[revol_asset]]  # revolving pool can be a list of assets 
                                              ,[{"CDR":0.01}]]}   # revolving pool may have different pool performance assumption
                         ,{"CDR":0.0012}],
             read=True)

Revolving Buy
^^^^^^^^^^^^^^^

Pricing an revolving asset would have a huge impact on the pool cashflow . 

.. code-block:: python 

    ["buyAsset",<PricingMethod>,<Account>,None]

:ref:`Pricing Method` :

* price an asset with balance factor `["Current|Defaulted",0.95,0]` means , if the asset has a current balance of 100, then the price would be 100*0.95 = 95
* price an asset with curve, with a pricing curve supplied, price an asset by discount cashflow of the asset

.. code-block:: python 

  ["IfElse"  # 
   ,["status","Revolving"]
   ,[["transferBy",{"formula":("substract",("bondBalance",),("poolBalance",))}
                  ,"distAcc",'revolBuyAcc']
    ,["buyAsset",["Current|Defaulted",1.0,0],"revolBuyAcc",None] # <--- action of buying revolving assets
    ,["payResidual","distAcc","Sub"] ]
   ,[["payPrin","distAcc",["A"]]
    ,["payPrin","distAcc",["Sub"]]
    ,["payFeeResidual", "distAcc", "bmwFee"]]]]

Visualize the cash `flow`
---------------------------

Waterfall rules can be complex and headache.
Luckily `absbox` is gentle enough to provide candy function to visualize the fund allocation.

`absbox` is using `Graphviz <https://graphviz.org/>`_  , 
pls make sure it was installed as well as python wrapper `graphviz <https://pypi.org/project/graphviz/>`_ 

Let's use the example -> :ref:`BMW Auto Deal 2023-01`


.. code-block:: python 

  from absbox.local.chart import viz
  
  viz(BMW202301) # that's it ,done !

.. raw:: html
  :width: 600
  :file: img/bmw_viz.svg

  
