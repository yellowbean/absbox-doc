Analytics
====

.. autosummary::
   :toctree: generate

.. warning::
    This page is Working in progress



Setup a API
-----

.. code-block:: python

   from absbox import API,save
   from absbox.local.china import 信贷ABS,show
   localAPI = API("https://deal-bench.xyz/api")


``"https://deal-bench.xyz/api"`` Can be depolyed in user's local enviroment

.. note::
   the remote engine exposes REST Service ,`absbox` send deal models and cashflow projection assumptions to that server.
   The engine code was hosted at `Hastructure <https://github.com/yellowbean/Hastructure>`_


Once the API was instantised call "``run()``" to project cashflow and pricing the bond

.. code-block:: python

  localAPI.run(test01, 
               assumptions=[{"CPR":0.01}  
                           ,{"CDR":0.01}  
                           ,{"Recovery":(0.7,18)}],  
               pricing={"PVDay":"2023-06-22"
                       ,"Curve":[["2020-01-01",0.025]]},
               read=True
              )
