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


Once the API was instantised ,call ``run()`` to project cashflow and pricing the bond

.. code-block:: python

  localAPI.run(test01, 
               assumptions=[{"CPR":0.01}  
                           ,{"CDR":0.01}  
                           ,{"Recovery":(0.7,18)}],  
               pricing={"PVDay":"2023-06-22"
                       ,"Curve":[["2020-01-01",0.025]]},
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
^^^^^^^^^^^^

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


