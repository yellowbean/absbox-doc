Analytics
====

.. autosummary::
   :toctree: generate

.. warning::
    This page is Working in progress



Setup a API
-----

.. code-block:: python

   from absbox import API
   localAPI = API("https://deal-bench.xyz/api")


.. note::
   User can pull the docker image to run his/her own in-house environment


.. note::
   the remote engine exposes REST Service , ``absbox`` send deal models and cashflow projection assumptions to that server.
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
----
the `run()` function will return a dict

.. code-block:: python

   r = localAPI.run(test01, 
                    assumptions=[{"CPR":0.01}  
                                ,{"CDR":0.01}  
                                ,{"Recovery":(0.7,18)}],  
                    pricing={"PVDay":"2023-06-22"
                            ,"Curve":[["2020-01-01",0.025]]},
                    read=True)

Bond Cashflow 
^^^^

.. code-block:: python

   r['bonds'].keys() # all bond names
   r['bonds']['A1'] # cashflow for bond `A1`

Fee Cashflow
^^^^

.. code-block:: python

   r['fees'].keys() # all fee names
   r['fees']['trusteeFee'] 

Account flow
^^^^

.. code-block:: python

   r['accounts'].keys() # all account names
   r['accounts']['acc01'] 


Pool Cashflow 
^^^^

.. code-block:: python

   r['pool']['flow'] # pool cashflow 


Bond Pricing 
^^^^

if passing `pricing` in the `run`, then response would have a key `pricing`

.. code-block:: python

   r['pricing']


