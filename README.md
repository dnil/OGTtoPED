OGTtoPED
========

Import OGT sample information workbook in Excel format, and extract affectedness status and basic family ped info for sample IDs.

Usage
-----

`python OGTtoPED.py data/Sequencing_sample_Batch_150108_KLR.xlsx`


    usage: OGTtoPED.py [-h] [-D] orderform

    positional arguments:
        orderform    OGT order form containing sample IDs, affectedness status and
                     family grouping.
    
    optional arguments:
      -h, --help   show this help message and exit
      -D, --debug  Enable DEBUG output.



Installation and dependencies
-----------------------------

Good Practice dictates the use of a virtual environment for python, not to mess with the system python or your pet development project.

`pip install virtualenv`

`virtualenv venv`

`source venv/bin/activate`

`pip install openpyxl`

