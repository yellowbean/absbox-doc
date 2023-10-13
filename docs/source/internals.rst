Internals 
===========

Asset Cashflow Projection Document
-----------------------------------

Performing Asset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mortgage/Loan/Installment
"""""""""""""""""""""""""""

* determine the ``projection dates``
  
  * ``start date`` -> There is a field in asset present the `origination date` ,which means the date when asset came into existance.
  * ``(original/scheduled) payment dates`` -> Then, cashflow engine will generate a vector of payment dates bases on `origination date` and `payment frequency`
  * ``remaining payment dates`` -> base on the input field `remaining terms`, engine will trancate the `payment dates` to get `remaining payment dates`

* project cashflow with assumptions
  
  * ``projected cashflow`` -> Given `remaining payment dates` and `current balance` , then engine will calculate cashflow with assumption starting from `remaining payment dates`

* truncate the cashflow via `cutoff date`

  * `projected cashflow` was truncated via `cutoff date` ,that's the cashflow of asset which flows into the SPV

Non-Performing Asset(WIP)
""""""""""""""""""""""

(WIP)

.. graphviz::
    :name: sphinx.ext.graphviz
    :caption: Sphinx and GraphViz Data Flow
    :alt: How Sphinx and GraphViz Render the Final Document
    :align: center

     digraph "sphinx-ext-graphviz" {
         size="6,4";
         rankdir="LR";
         graph [fontname="Verdana", fontsize="12"];
         node [fontname="Verdana", fontsize="12"];
         edge [fontname="Sans", fontsize="9"];

         sphinx [label="Sphinx", shape="component",
                   href="https://www.sphinx-doc.org/",
                   target="_blank"];
         dot [label="GraphViz", shape="component",
              href="https://www.graphviz.org/",
              target="_blank"];
         docs [label="Docs (.rst)", shape="folder",
               fillcolor=green, style=filled];
         svg_file [label="SVG Image", shape="note", fontcolor=white,
                 fillcolor="#3333ff", style=filled];
         html_files [label="HTML Files", shape="folder",
              fillcolor=yellow, style=filled];

         docs -> sphinx [label=" parse "];
         sphinx -> dot [label=" call ", style=dashed, arrowhead=none];
         dot -> svg_file [label=" draw "];
         sphinx -> html_files [label=" render "];
         svg_file -> html_files [style=dashed];
     }