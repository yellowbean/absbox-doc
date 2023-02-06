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

Assumptions is composed of three categories:

* Asset Performance 
  
  Different asset class would need different combination of performance assumptions.

 * Mortgage / Loan / Installment
 * Lease 

* Deal Aussumption
  
 * Call Assumption 
   
   .. code-block:: python
   
     {"CleanUp":[{"poolBalance":200}
                 ,{"bondBalance":100}
                 ,{"poolFactor":0.03}
                 ,{"bondFactor":0.03}
                 ,{"afterDate":0.03}
                 ,{"or":[{"afterDate":0.03}
                         ,{"poolFactor":0.03}]}
                 ,{"and":[{"afterDate":0.03}
                         ,{"poolFactor":0.03}]}
                 ,{"and":[{"afterDate":0.03}
                          ,{"or":
                             [{"poolFactor":0.03}
                             ,{"bondBalance":100}]}]}
     ]}
   
 * Interest Rate Assumption
   
   .. code-block:: python
   
   {"Rate":["LIBOR1M":[["2022-01-01",0.05]
                      ,["2023-01-01",0.06]
                      ]]}
   
   {"Rate":["LIBOR1M":0.05]}

   

* Debug
 * `{stopRun:"2020-01-01"}` -> stop cashflow projection at `2020-01-01`


Running
--------------

Running a deal 
^^^^^^^^^^^^^^^^^

Once the API was instantised ,call ``run()`` to project cashflow and pricing the bond

.. code-block:: python

  localAPI.run(test01, 
               assumptions=[{"CPR":0.01}  
                           ,{"CDR":0.01}  
                           ,{"Recovery":(0.7,18)}],  
               pricing={"PVDay":"2023-06-22"
                       ,"Curve":[["2020-01-01",0.025]]},
               read=True)

Running a Pool 
^^^^^^^^^^^^^^^^^

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
                    pricing={"PVDay":"2023-06-22"
                            ,"Curve":[["2020-01-01",0.025]]},
                    read=True)


the `runPool()` function will return cashflow for a pool, user need to specify `english` as second parameter to `API` class to enable return header in English

.. code-block:: python

   localAPI = API("http://localhost:8081",'english')

   mypool = {'assets':[
          ["Lease"
           ,{"fixRental":1000,"originTerm":12,"freq":["DayOfMonth",12]
            ,"remainTerm":10,"originDate":"2021-02-01"}]
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