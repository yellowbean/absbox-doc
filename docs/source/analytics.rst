Analytics
==============

.. autosummary::
   :toctree: generate

.. warning::
    This page is Working in progress



Setup a API
----------------

here is a list of available servers at `absbox.org <https://absbox.org>`_

.. code-block:: python

   from absbox import API
   localAPI = API("https://absbox.org/api/latest")
   
   # setting default language
   localAPI = API("https://absbox.org/api/latest",lang='english')


.. note::
   User can pull the docker image to run his/her own in-house environment


.. note::
   the remote engine exposes RESTful Service , ``absbox`` send deal models and cashflow projection assumptions to that server.
   The engine code was hosted at `Hastructure <https://github.com/yellowbean/Hastructure>`_


Asset Performance Assumption
----------------------------------------

Assumpitions are required to set when running stressed scenario as well as getting specific outputs other than cashflow.

There are two type of assumptions:

* Assumptions for performance of asset
* Assumptions for running a deal

Mortgage/Loan/Installment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
   <delinq assumption> is not implemented yet ,it only serves as a place holder


Here is sample which used to set ``Pool`` level assumption on ``Mortgage`` asset class.


.. code-block:: python

   r = localAPI.run(deal
                  ,poolAssump = ("Pool",("Mortgage",<default assump>,<prepay assump>,<recovery assump>,<extra assump>)
                                          ,<delinq assumption>
                                          ,<defaulted assumption>)
                  ,runAssump = None
                  ,read=True)

   r = localAPI.run(deal
                  ,poolAssump = ("Pool",("Loan",<default assump>,<prepay assump>,<recovery assump>,<extra assump>)
                                          ,<delinq assumption>
                                          ,<defaulted assumption>)
                  ,runAssump = None
                  ,read=True)

   r = localAPI.run(deal
                  ,poolAssump = ("Pool",("Installment",<default assump>,<prepay assump>,<recovery assump>,<extra assump>)
                                          ,<delinq assumption>
                                          ,<defaulted assumption>)
                  ,runAssump = None
                  ,read=True)

Notes:

* ``Pool`` ,means the assumption will be applied to ``all`` the assets in the pool
* ``Mortgage`` ,means the it's assumption applied to ``Mortgage`` asset class
  
  for `Performing Asset`

  * ``<default assump>``   -> default assumption for performing asset: like ``{"CDR":0.01}``
  
    * ``{"CDR":0.01}`` means 1% in annualized of current balance will be defaulted at the end of each period
    * ``{"CDR":[0.01,0.02,0.04]}`` means a vector of CDR will be applied since the asset snapshot date (determined by ``remain terms``)
  * ``<prepay assump>``    -> prepayment assumption for performing asset : like ``{"CPR":0.01}``
  
    * ``{"CPR":0.01}`` means 1% in annualized of current balance will be prepay at the end of each period
    * ``{"CPR":[0.01,0.02,0.04]}`` means a vector of CPR will be applied since the asset snapshot date (determined by ``remain terms``)
  * ``<recovery assump>``  -> recovery assumption for performing asset : like ``{"Rate":0.7,"Lag":18}``
    
    * ``{"Rate":0.7,"Lag":18}`` means 70% of current balance will be recovered at 18 periods after defaulted date

  for `Non-Performing Asset`
  
  * ``<delinq assump>``       -> assumption to project cashflow of asset in ``delinquent`` status
    
    *reserve for future use* : always use ``None``

  * ``<defaulted assump>``    -> assumption to project cashflow of asset in ``defaulted`` status
    i.e 

      .. code-block:: python 
      
          ("Defaulted":[0.5,4,[0.5,0.2,0.3]])

      which says:

      * the recovery percentage is 50% of current balance
      * the recovery starts at 4 periods after defaulted date
      * the recovery distribution is 50%,20% and 30%

Extra Stress 
""""""""""""""

Users are enable to apply:

* apply extra haircut by percentage to pool cashflow
* apply time series stress on prepay or default curve

.. warning::
    Extra stress only supports `Mortgage` assumption

.. code-block:: python

   r = localAPI.run(deal
                  ,poolAssump = ("Pool",("Mortgage",{"CDR":0.01}
                                                   ,{"CPR":0.01}
                                                   ,None
                                                   ,{"defaultFactor":[["2020-10-01",1.05]
                                                                      ,["2022-10-01",1.15]]
                                                     ,"prepayFactor":[["2020-10-01",1.05]
                                                                      ,["2022-10-01",1.15]]
                                                     ,"haircuts":[("Interest",0.05)]})
                                          ,None
                                          ,None)
                  ,runAssump = None
                  ,read=True)



Lease
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   r = localAPI.run(deal
                  ,poolAssump = ("Pool",("Lease",<turnover gap>,<rental assump>,<end date>)
                                          ,<delinq assumption>
                                          ,<defaulted assumption>
                                          )
                  ,runAssump = None
                  ,read=True)

Notes:

  * ``<turnover gap>`` ->  assumption on gap days between new lease and old lease
  * ``<rental assump>`` -> describe the rental increase/decrease over time
  * ``<end date>`` -> the date when lease projection ends 

Assumption on Asset Level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As suggested above, the assumption would apply to all the asset of deals. But user has the abliity to set assumption on asset level.


.. code-block:: python
   
   #syntax 
   ("ByIndex"
     ,([<asset id>],(<default assump>,<prepay assump>,<recvoery assump>))
     ,([<asset id>],(<default assump>,<prepay assump>,<recvoery assump>))
     ,....
     )

i.e 


.. code-block:: python
  
  myAsset1 = ["Mortgage"
              ,{"originBalance": 12000.0
               ,"originRate": ["fix",0.045]
               ,"originTerm": 120
               ,"freq": "monthly"
               ,"type": "level"
               ,"originDate": "2021-02-01"}
              ,{"currentBalance": 10000.0
               ,"currentRate": 0.075
               ,"remainTerm": 80
               ,"status": "current"}]
  myAsset2 = ["Mortgage"
              ,{"originBalance": 12000.0
               ,"originRate": ["fix",0.045]
               ,"originTerm": 120
               ,"freq": "monthly"
               ,"type": "level"
               ,"originDate": "2021-02-01"}
              ,{"currentBalance": 10000.0
               ,"currentRate": 0.075
               ,"remainTerm": 80
               ,"status": "current"}]
  
  myPool = {'assets':[myAsset1,myAsset2],
            'cutoffDate':"2022-03-01"}
  
  Asset01Assump = (("Mortgage"
                   ,{"CDR":0.01} ,{"CPR":0.1}, None, None)
                   ,None
                   ,None)
  Asset02Assump = (("Mortgage"
                   ,{"CDR":0.2} ,None, None, None)
                   ,None
                   ,None)
  
  AssetLevelAssumption = ("ByIndex"
                          ,([0],Asset01Assump)
                          ,([1],Asset02Assump))
  
  r = localAPI.runPool(myPool
                     ,poolAssump=AssetLevelAssumption
                     ,read=True)
  
  # asset cashflow
  r[0]



Deal Assumption
----------------------------------------

``Deal Assumption`` is just list of tuples passed to ``runAssump`` argument.

.. code-block:: python

  r = localAPI.run(deal
                   ,poolAssump = None 
                   ,runAssump = [("stop","2021-01-01")
                                ,("call",("CleanUp",("poolBalance",200)))
                                ,.....]
                   ,read=True)

Stop Run
^^^^^^^^^^^^^^

cashflow projection will stop at the date specified.

.. code-block:: python

  ("stop","2021-01-01")



Project Expense
^^^^^^^^^^^^^^

a time series of expense will be used in cashflow projection.

.. code-block:: python

  # fee in the deal model
  ,(("trusteeFee",{"type":{"fixFee":30}})
      
      ,("tsFee",{"type":{"customFee":[["2024-01-01",100]
                                    ,["2024-03-15",50]]}})
      ,("tsFee1",{"type":{"customFee":[["2024-05-01",100]
                                      ,["2024-07-15",50]]}})     
     )

  # assumption to override 
  r = localAPI.run(test01
               ,runAssump=[("estimateExpense",("tsFee"
                                               ,[["2021-09-01",10]
                                                ,["2021-11-01",20]])
                                              ,("tsFee1"
                                               ,[["2021-12-01",10]
                                                ,["2022-01-01",20]])
                           )]
               ,read=True)                    

Call When
^^^^^^^^^^^^^^

Assumptions to call the deal. 

* either of condtion was met, then the deal was called.
* the call test was run on `distribution day`, which is describle by `payFreq` on :ref:`Deal Dates`

.. code-block:: python
  
  ("call",{"poolBalance":200},{"bondBalance":100})

  ("call",{"poolBalance":200} # clean up when pool balance below 200
         ,{"bondBalance":100} # clean  up when bond balance below 100
         ,{"poolFactor":0.03} # clean up when pool factor below 0.03
         ,{"bondFactor":0.03} # clean up when bond factor below 0.03
         ,{"afterDate":"2023-06-01"} # clean up after date 2023-6-1
         ,{"or":[{"afterDate":"2023-06-01"} # clean up any of them met
                 ,{"poolFactor":0.03}]}
         ,{"and":[{"afterDate":"2023-06-01"} # clean up all of them met
                 ,{"poolFactor":0.03}]}
         ,{"and":[{"afterDate":"2023-06-01"} # nested !! 
                  ,{"or":
                     [{"poolFactor":0.03}
                     ,{"bondBalance":100}]}]}
     

Revolving Assumption
^^^^^^^^^^^^^^

User can set assumption on revolving pool with two compoenents: assets and performance assumption.

pool of revolving assets
    :code:`["constant",asset1,asset2....]`

    there are three types of revolving pools:
      * constant : assets in the pool will not change after buy
      * static : assets size will be shrink after buy
      * curve : assets available for bought will be determined by a time based curve

assumption for revolving pool
    :code:`<same as pool performance>` 

.. warning::
   the assumption for revolving pool only supports "Pool Level"

.. code-block:: python

      ("revolving"
       ,["constant",revol_asset]
       ,("Pool",("Mortgage",{"CDR":0.07},None,None,None)
                 ,None
                 ,None))


Interest Rate
^^^^^^^^^^^^^^

set interest rate assumptions for cashflow projection. 

.. code-block:: python

   from absbox.local.generic import Generic
   ## interest on asset
   test01 = Generic(
      "TEST01"
      ,{"cutoff":"2021-03-01","closing":"2021-06-15","firstPay":"2021-07-26"
      ,"payFreq":["DayOfMonth",20],"poolFreq":"MonthEnd","stated":"2030-01-01"}
      ,{'assets':[["Mortgage"
         ,{"originBalance":2200,"originRate":["floater",0.045,{"index":"SOFR3M"
                                             ,"spread":0.02
                                             ,"reset":"QuarterEnd"}]
            ,"originTerm":30
            ,"freq":"Monthly","type":"Level","originDate":"2021-02-01"}
            ,{"currentBalance":2200
            ,"currentRate":0.08
            ,"remainTerm":25
            ,"status":"current"}]]}
      ,(("acc01",{"balance":0}),)
      ,(("A1",{"balance":1000
               ,"rate":0.07
               ,"originBalance":1000
               ,"originRate":0.07
               ,"startDate":"2020-01-03"
               ,"rateType":{"Fixed":0.08}
               ,"bondType":{"Sequential":None}})
         ,("B",{"balance":1000
               ,"rate":0.0
               ,"originBalance":1000
               ,"originRate":0.07
               ,"startDate":"2020-01-03"
               ,"rateType":{"Fixed":0.00}
               ,"bondType":{"Equity":None}
               }))
      ,(("trusteeFee",{"type":{"fixFee":30}}),)
      ,{"amortizing":[
            ["calcAndPayFee","acc01",['trusteeFee']]
            ,["accrueAndPayInt","acc01",["A1"]]
            ,["payPrin","acc01",["A1"]]
            ,["payPrin","acc01",["B"]]
            ,["payIntResidual","acc01","B"]
      ]}
      ,[["CollectedInterest","acc01"]
         ,["CollectedPrincipal","acc01"]
         ,["CollectedPrepayment","acc01"]
         ,["CollectedRecoveries","acc01"]])


   r = localAPI.run(test01
                  ,runAssump=[("interest"
                              ,("LPR5Y",0.04)
                              ,("SOFR3M",[["2021-01-01",0.025]
                                          ,["2022-08-01",0.029]]))]
                  ,read=True)


Inspection
^^^^^^^^^^^^^^
Transparency matters ! For the users who are not satisfied with cashflow numbers but also having curiosity of the intermediary numbers, like `bond balance`, `pool factor` .

Users are able to query values from any point of time ,using syntax ``(<DatePattern>,<Formula>)``

* any point of time -> annoate by :ref:`DatePattern`
* values -> annoate by :ref:`Formula`


.. code-block:: python 

   ("inspect",("MonthEnd",("poolBalance",))
             ,("QuarterFirst",("bondBalance",))
             ,....)

To view these data as map, with formula as key and a dataframe with time series as value. 

.. code-block:: python
   
    # A map 
    r['result']['inspect'] 

    # a dataframe
    r['result']['inspect']['<CurrentBondBalance>'] 

But, the values are a dataframe with single column, how to view all the variables in a single dataframe ? Here is the answer :

.. code-block:: python
   
   from absbox.local.util import unifyTs

   unifyTs(r['result']['inspect'].values())


.. image:: img/inspect_unified.png
  :width: 400
  :alt: inspect_unified




Financial Reports
^^^^^^^^^^^^^^^^^^^

User just need to specify the ``dates`` of financial statement by :ref:`DatePattern`


.. code-block:: python 

   ("report",{"dates":"MonthEnd"})

to view results

.. code-block:: python 

   r['results']['report']['balanceSheet']

   r['results']['report']['cash']

Pricing
^^^^^^^^^^^

* User can provide a pricing curve and a pricing data to argument `pricing`,which all future bond cashflow will be discounted at that date with the curve provided.

.. code-block:: python

   ("pricing"
     ,{"date":"2021-08-22"
       ,"curve":[["2021-01-01",0.025]
                ,["2024-08-01",0.025]]})

* Caculate Z-spread  

User need to provide a ``{<bond name>:(<price date>,<price>)}``
The engine will calculate the how much spread need to added into ``curve``, then the PV of 
bond cashflow equals to ``<price>``

.. code-block:: python

   ("pricing"
     ,{"bonds":{"A1":("2021-07-26",100)}
      ,"curve":[["2021-01-01",0.025]
               ,["2024-08-01",0.025]]})


Running
--------------

Running
  Means sending request to backend engine server. A request has three elmenets:
   * API instance 
   * Assumptions

     * Pool performance assumptions
     * Deal assumptions (May include Interest Rate / Clean Up Call)


Running a deal 
^^^^^^^^^^^^^^^^^

Once the API was instantised ,call ``run()`` to project cashflow and price the bonds

When the deal was trigger for a run:

* Project pool cashflow from the pool assumptions supplied by user 
* Feed pool cashflow to waterfall
* Waterfall distributes the fund to bonds, expenses, etc.

params:
   * ``deal`` : a deal instance
   * ``poolAssump`` : pool performance assumption, passing a map if run with multi scenaro mode
   * ``runAssump`` : deal assumptions 
   * ``read`` : if `True` , will try it best to parse the result into `DataFrame`

returns:
   * a map with keys of components like:
  
     * ``bonds``
     * ``fees`` 
     * ``accounts``
     * ``pool``
     * ``result``
     * ``pricing``

.. image:: img/deal_cycle_flow.png
  :width: 600
  :alt: version


.. code-block:: python

  localAPI.run(test01,
               poolAssump=("Pool",("Mortgage",{"CPR":0.01},{"CDR":0.01},{"Rate":0.7,"Lag":18})
                                 ,None
                                 ,None),
               runAssump =[("pricing"
                            ,{"PVDate":"2021-08-22"
                            ,"PVCurve":[["2021-01-01",0.025]
                                       ,["2024-08-01",0.025]]})],
               read=True)


Running a pool of assets 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

user can project cashflow for a pool only, with ability to set pool performance assumption.

params:
    * ``assets`` : a list of ``asset`` objects
    * ``cutoffDate`` : a date which suggests all cashflow after that date will be shown
    * ``poolAssump`` : pool performance assumption, passing a map if run with multi scenaro mode
    * ``rateAssump`` : interest rate assumption
    * ``read`` : if `True` , will try it best to parse the result into `DataFrame`

returns:
   * (``<Pool Cashflow>``
   *  , ``<Pool History Stats>``)

Single Scenario
""""""""""""""""""

.. code-block:: python

   myPool = {'assets':[
               ["Mortgage"
               ,{"originBalance": 12000.0
               ,"originRate": ["fix",0.045]
               ,"originTerm": 120
               ,"freq": "monthly"
               ,"type": "level"
               ,"originDate": "2021-02-01"}
               ,{"currentBalance": 10000.0
               ,"currentRate": 0.075
               ,"remainTerm": 80
               ,"status": "current"}]],
            'cutoffDate':"2022-03-01"}

   r = localAPI.runPool(myPool
                     ,poolAssump=("Pool",("Mortgage",{"CDR":0.01},None,None,None)
                                       ,None
                                       ,None)
                     ,read=True)
   r[0] # pool cashflow
   r[1] # pool history stats before cutoff date

Multi Scenarios
""""""""""""""""""

If user pass scenario with a map , the response will be a map as well.

.. code-block:: python

  myPool = {'assets':[
              ["Mortgage"
              ,{"originBalance": 12000.0
              ,"originRate": ["fix",0.045]
              ,"originTerm": 120
              ,"freq": "monthly"
              ,"type": "level"
              ,"originDate": "2021-02-01"}
              ,{"currentBalance": 10000.0
              ,"currentRate": 0.075
              ,"remainTerm": 80
              ,"status": "current"}]],
           'cutoffDate':"2022-03-01"}
  
  
  multiScenario = {
      "Stress01":("Pool",("Mortgage",{"CDR":0.01},None,None,None)
                                      ,None
                                      ,None)
      ,"Stress02":("Pool",("Mortgage",{"CDR":0.05},None,None,None)
                                      ,None
                                      ,None)
  }
  
  r = localAPI.runPool(myPool
                      ,poolAssump = multiScenario
                      ,read=True)
  r["Stress01"][0]
  r["Stress02"][0]

Running a single asset 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

params:
    * ``cutoff date`` : only cashflow after `cutoff date` will be shown 
    * ``assets`` : a list of assets to project 
    * ``poolAssump`` : pool performance assumption
    * ``rateAssump`` : interest rate assumption
    * ``read`` : if `True` , will try it best to parse the result into `DataFrame`

returns:
   * (``<asset cashflow>``
   *  , ``<cumulative balance before cutoff date>``
   *  , ``<pricing result>``)  -> not implemented yet

.. code-block:: python

  myAsset = ["Mortgage"
            ,{"originBalance": 12000.0
             ,"originRate": ["fix",0.045]
             ,"originTerm": 120
             ,"freq": "monthly"
             ,"type": "level"
             ,"originDate": "2021-02-01"}
            ,{"currentBalance": 10000.0
             ,"currentRate": 0.075
             ,"remainTerm": 80
             ,"status": "current"}]

  r = localAPI.runAsset("2024-08-02"
                       ,[myAsset]
                       ,poolAssump=("Pool",("Mortgage",{'CDR':0.01},None,None,None)
                                          ,None
                                          ,None)
                       ,read=True)

  # asset cashflow
  r[0] 
  # cumulative defaults/loss/delinq before cutoff date
  r[1]

  # or just pattern match on the result
  (cf,stat,pricing) = localAPI.runAsset(....)


Getting cashflow
------------------

* the `run()` function will return a dict which with keys of components like `bonds` `fees` `accounts` `pool`
* the first argument to `run()` is an instance of `deal`

.. code-block:: python

   r = localAPI.run(test01, 
                    ......
                    read=True)


the `runPool()` function will return cashflow for a pool, user need to specify `english` as second parameter to `API` class to enable return header in English

.. code-block:: python

   localAPI = API("http://localhost:8081",lang='english')

   mypool = {'assets':[
                     ["Lease"
                     ,{"fixRental":1000,"originTerm":12,"freq":["DayOfMonth",12]
                        ,"remainTerm":10,"originDate":"2021-02-01","status":"Current"}]
              ],
             'cutoffDate':"2021-04-04"}




Bond Cashflow 
^^^^^^^^^^^^^^^^

.. code-block:: python

   r['bonds'].keys() # all bond names
   r['bonds']['A1'] # cashflow for bond `A1`

Bond Cashflow By Position
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  from absbox.local.util import positionFlow

  r = localAPI.run()
  
  positionFlow(r, {'A1':15000000.0} )


Fee Cashflow
^^^^^^^^^^^^^^

.. code-block:: python

   r['fees'].keys() # all fee names
   r['fees']['trusteeFee'] 

Account Cashflow
^^^^^^^^^^^^^^^^^

.. code-block:: python

   r['accounts'].keys() # all account names
   r['accounts']['acc01'] 


Pool Cashflow 
^^^^^^^^^^^^^^^

.. code-block:: python

   r['pool']['flow'] # pool cashflow 


Bond Pricing 
^^^^^^^^^^^^^

if passing `pricing` in the `run`, then response would have a key `pricing`

.. code-block:: python

   r['pricing']



Getting Results
---------------

``r['result']`` save the run result other than cashflow.

Status During Run
^^^^^^^^^^^^^^^^^^^^

it is not uncommon that `triggers` may changed deal status between `accelerated` `defaulted` `amorting` `revolving`.
user can check the `status` chang log via :

.. code-block:: python
   
   r["result"]["status"]

or user can cross check by review the account logs by (if changing deal status will trigger selecting different waterfall) :

.. code-block:: python
   
   r["accounts"]["<account name>"].loc["<date before deal status change>"]
   r["accounts"]["<account name>"].loc["<date after deal status change>"]


Variables During Waterfall 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If there is waterfall action in the waterfall 

.. code-block:: python
   
  ,["inspect","BeforePayInt bond:A1",("bondDueInt","A1")]


then the <Formula> value can be view in the ``result`` ``waterfallInspect``.

.. code-block:: python
   
  r['result']['waterfallInspect']




Sensitivity Analysis
----------------------

There are two types in sensitivity analysis in `absbox`: Either teaking on assumptions (left) or changing deal components (right)

.. image:: img/sensitivity_analysis.png
  :width: 600
  :alt: sensitivity


It is common to performn sensitivity analysis to get answers to:

* What are the pool performance in different scenarios ? 
* what if the call option was exercise in differnt date or different bond/pool factor ?
* what if interest rate curve drop/increase ?
* or any thing changes in the `assumption` ?

That's where we need to have a  `Multi-Scneario` run .

Multi-Scenario
^^^^^^^^^^^^^^^^^

if passing `assumptions` with a dict. Then the key will be treated as `secnario name`, the value shall be same as single scneario cases.

.. code-block:: python

   myAssumption = ("Pool",("Mortgage",{"CDR":0.01},None,None,None)
                                   ,None
                                   ,None)
   
   myAssumption2 = ("Pool",("Mortgage",None,{"CPR":0.01},None,None)
                                   ,None
                                   ,None)
   
   r = localAPI.run(test01
               ,poolAssump={"00":myAssumption
                           ,"stressed":myAssumption2}
               ,read=True)

User shall able to access the each scenario's response by just by `scenario name`

.. code-block:: python
   
   r["00"]
   r["stressed"]

There are couple candy function user can view the data field from all the scenarios:

.. code-block:: python
   
   from absbox.local.util import flow_by_scenario

   flow_by_scenario(rs,["pool","flow","Interest"])
   flow_by_scenario(rs,["bonds","A1","principal"])
   flow_by_scenario(rs,["bonds","A1", ["principal","cash"]])
   flow_by_scenario(rs,["pricing","A1"],node="idx")


Multi-Structs
^^^^^^^^^^^^^^^^^

In the structuring stage:

* what if sizing a larger bond balance for Bond A ?
* what if design a differnt issuance balance for tranches ? 
* what if include less/more assets in the pool ?
* what if changing a waterfall payment sequesnce ? 
* what if adding a trigger ? 
* or anything in changes in the `deal` component ?

That's where we need to have a `Multi-Structs` run .


.. code-block:: python

  r = localAPI.runStructs({"A":test01,"B":test02},read=True)

  # user can get different result from `r`

  # deal run result using structure test 01
  r["A"]

  # deal run result using structure test 02
  r["B"]

Retriving Results
^^^^^^^^^^^^^^^^^^^^^

The result returned from sensitivity run is just a map, with key as identifer for each scenario, the value is the same as single run. 

To access same component from different sceanrio : 

.. code-block:: python

  r # r is the sensitivity run result 
  
  # get bond "A1" cashflow from all the scenario ,using a list comprehension
  {k: v['bonds']["A1"] for k,v in r.items() }

  # get account flow "reserve_account_01"
  {k: v['accounts']["reserve_account_01"] for k,v in r.items() }

  

IRR 
------------------

powered by `pyxirr`, user have option to calculate the IRR of a bond.

* 1st parameter should pass the dataframe of bond flow 
* 2nd `init` represent `initial investment` a tuple with first as date of invesment and second as monetary amount of investment


.. code-block:: python

   from absbox.local.util import irr
   irr(r['bonds']['A1'],init=('2021-06-15',-70))




