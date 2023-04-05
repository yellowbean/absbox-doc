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
   * - "Monthly"
     - freq
     -
   * - "Amortization Type"
     - type
     -
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
                ,'Loan Term','Remaining Months to Maturity','Index', ,'Current Interest Rate','Days Delinquent']]


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
  
  loans = [["Mortgage"
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



How to structuring a deal<WIP>
-------------------------------------------

Strucuring a deal may looks intimidating, while the process is simple: 

1. Given a base line deal, user run it and keep the result of interest:
   A. Maybe bond cashflow 
   B. Maybe bond pricing result
   C. Maybe trigger event 

2. User create a bunch of new components and swap them into the deal, run the deal again and compare the new result of interest with ones generated from baseline model.





Build a base model
^^^^^^^^^^^^^^^^^^^

It is recommended to build a base model to be serve as a baseline for furthur analysis.

Tweaking by running
^^^^^^^^^^^^^^^^^^^^

User can either setup deal model by tweaking one component or mutiple components.
Once these new components were setup, user can `replace` these new components to the deals ,resulting multiple instance of deals.
Run these deals with engine and compare the resuls. The difference shows how variuos captial structure or trigger /waterfall component would impact on the result of interest.




How to stress pool by stratification <WIP>
-------------------------------------------
TODO
