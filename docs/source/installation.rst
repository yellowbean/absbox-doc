Installation
===============

.. autosummary::
   :toctree: generated

.. warning::
  `absbox`is heavily using `match clause` which was introduced in Python3.10
  Please make sure you are using *Python3.10* and above

Using pip
--------------

.. code-block:: console

    pip install absbox

Upgrade `absbox` package to latest
^^^^^^^^^^^^^^^^^^

.. code-block:: console

    pip install -U absbox

Check version
^^^^^^^^^^^^^^^

.. code-block:: console 

    pip show absbox 

which shows current version of `absbox` 

.. image:: img/package_version.png
  :width: 500
  :alt: version

Github
--------------

User can install from Github.com as it is actively fixing new bugs and developing new features.
Documents and sample code in this site are being test against with code from github.com

.. code-block:: console

    pip install -U git+https://github.com/yellowbean/AbsBox.git@main


Public Server vs Self-hosted
-----------------------------

``absbox`` needs to connect a engine behind the scene. User can choose a public one or use it's own if user is looking for more privacy and performance.

.. code-block:: python

   from absbox import API
   localAPI = API("https://deal-bench.xyz/api")

* For public server list, pls visit `absbox.org <https://absbox.org>`_
* If user want to have a self-hosted server 
    * user can build one from source code `Hastructure <https://github.com/yellowbean/Hastructure>`_
    * or using docker 
  
.. code-block:: bash

  docker pull yellowbean/hastructure
  docker run yellowbean/hastructure


.. note ::
  ``absbox`` uses ``pandas`,``requests`` for data processing and service call.

.. note ::
  ``absbox`` uses ``pickle`` to store deal files.
