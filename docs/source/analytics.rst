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


.. note::
   User can pull the docker image to run his/her own in-house environment


.. note::
   the remote engine exposes RESTful Service , ``absbox`` send deal models and cashflow projection assumptions to that server.
   The engine code was hosted at `Hastructure <https://github.com/yellowbean/Hastructure>`_


Setting Assumption
--------------------

Assumpitions are just a *LIST*,  Assumptions fall into three categories:

Asset Performance 
^^^^^^^^^^^^^^^^^^^

Different asset class would need different combination of performance assumptions.

* Mortgage / Loan / Installment
 * Default Rate 
 * Prepayment Rate 
 * Reocvery/Recovery Lag 

* Lease 
 * Rental increase curve 
 * Rental gap in months 

User are able to set a constant value 

.. code-block:: python

  localAPI.run(test01,
             assumptions=[{"CPR":0.01}
                         ,{"CDR":0.01}
                         ,{"Recovery":(0.7,18)}],
             read=True)

User are able to set assumptions by curves

.. code-block:: python

  localAPI.run(test01,
             assumptions=[{"CPR":[0.02,0.02,0.03]}
                         ,{"CDR":[0.01,0.015,0.021]}
                         ,{"Recovery":(0.7,18)}],
             read=True)


* Lease 
 * Rental Increase
 * Rental Gaps

Deal Assumption
^^^^^^^^^^^^^^^^^^^
  
* Call Assumption 
   
   .. code-block:: python
   
     {"CleanUp":[{"poolBalance":200} # clean up when pool balance below 200
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
     ]}
   
* Interest Rate Assumption
   
   .. code-block:: python
   
     # vectorized/curve based assumption
     {"Rate":["LIBOR1M":[["2022-01-01",0.05]
                        ,["2023-01-01",0.06]
                        ]]}
     
     # constant assumption
     {"Rate":["LIBOR1M":0.05]}
   

Debug
^^^^^^^^^^

* Stop Run By Date

   .. code-block:: python
      # stop cashflow projection at `2020-01-01`
      {stopRun:"2020-01-01"} 


Running
--------------

Running a deal 
^^^^^^^^^^^^^^^^^

Once the API was instantised ,call ``run()`` to project cashflow and price the bonds

.. code-block:: python

  localAPI.run(test01,
             assumptions=[{"CPR":0.01}
                         ,{"CDR":0.01}
                         ,{"Recovery":(0.7,18)}],
             pricing={"PVDate":"2021-08-22"
                      ,"PVCurve":[["2021-01-01",0.025]
                                 ,["2024-08-01",0.025]]},
             read=True)

passing `read` with `True`, it will try it best to parse the result into `DataFrame`


Running a pool of assets 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

user can project cashflow for a pool only, with ability to set pool performance assumption .
a pool is a map with two keys:

* ``assets`` : a list of ``asset`` objects
* ``cutoffDate`` : a date which suggests all cf after will be shown

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
  
  localAPI.runPool(myPool, 
                 assumptions=[{"CPR":0.01}  
                             ,{"CDR":0.01}  
                             ,{"Recovery":(0.7,18)}],  
                 read=True)


Getting cashflow
------------------

* the `run()` function will return a dict which with keys of components like `bonds` `fees` `accounts` `pool`
* the first argument to `run()` is an instance of `deal`

.. code-block:: python

   r = localAPI.run(test01, 
                    assumptions=[{"CPR":0.01}  
                                ,{"CDR":0.01}  
                                ,{"Recovery":(0.7,18)}],  
                    pricing={"PVDate":"2023-06-22"
                            ,"PVCurve":[["2020-01-01",0.025]]},
                    read=True)


the `runPool()` function will return cashflow for a pool, user need to specify `english` as second parameter to `API` class to enable return header in English

.. code-block:: python

   localAPI = API("http://localhost:8081",'english')

   mypool = {'assets':[
          ["Lease"
           ,{"fixRental":1000,"originTerm":12,"freq":["DayOfMonth",12]
            ,"remainTerm":10,"originDate":"2021-02-01","status":"Current"}]
            ],
          'cutoffDate':"2021-04-04"}

   localAPI.runPool(mypool,assumptions=[])



Bond Cashflow 
^^^^^^^^^^^^^^^^

.. code-block:: python

   r['bonds'].keys() # all bond names
   r['bonds']['A1'] # cashflow for bond `A1`

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


Multi-Scenario
-----------------

if passing `assumptions` with a dict. Then the key will be treated as `secnario name`, the value shall be same as single scneario cases.

.. code-block:: python

   myAssumption = [{"CPR":0.0}
                   ,{"CDR":0.00}]
   
   myAssumption2 = [{"CPR":0.01}
                   ,{"CDR":0.1} ]
   
   r = localAPI.run(test01
               ,assumptions={"00":myAssumption,"stressed":myAssumption2}
               ,read=True)

User shall able to access the each scenario's response by just by `scenario name`

.. code-block:: python
   
   r["00"]
   r["stressed"]


IRR 
------------------

powered by `pyxirr`, user have option to calculate the IRR of a bond.

* 1st parameter should pass the dataframe of bond flow 
* 2nd `init` represent `initial invesment` a tuple with first as date of invesment and second as monetary amount of investment


.. code-block:: python

   from absbox.local.util import irr
   irr(r['bonds']['A1'],init=('2021-06-15',-70))


Status During Run
--------------------

it is not uncommon that `triggers` may changed deal status between `accelerated` `defaulted` `amorting` `revolving`.
user can check the `status` chang log via :

.. code-block:: python
   
   r["result"]["status"]

or user can cross check by review the account logs by (if changing deal status will trigger selecting different waterfall) :

.. code-block:: python
   
   r["accounts"]["<account name>"].loc["<date before deal status change>"]
   r["accounts"]["<account name>"].loc["<date after deal status change>"]





