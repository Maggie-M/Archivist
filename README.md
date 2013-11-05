======================
Continuum Store Tester
======================

========
Overview
========
The store tester is used to check the md5 and file size of any version of Anaconda against the expected md5 and size listed in the archive.

===
Use
===

From the command line, run the script, giving the version of Anaconda as an argument

.. code-block:: bash

    $ python store_test.py 1.5.0

Each version of Anaconda meeting this requirement will be downloaded from the Continuum archives, then checked.

============
Dependencies
============

`beautifulsoup4 <http://www.crummy.com/software/BeautifulSoup/>`_
`termcolor <https://pypi.python.org/pypi/termcolor>`_

====
TODO
====

Add a progress bar for downloads.

Automated license checking.

