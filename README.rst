======================
Continuum Store Tester
======================

========
Overview
========


The store tester is used to check the md5 and file size of any version of `Anaconda <https://store.continuum.io/cshop/anaconda/>`_ against the expected md5 and size listed in the archive.

===
Use
===

From the Store-test directory, run the script, giving the desired version of Anaconda as an argument:

.. code-block:: bash

    $ python store_test.py 1.5.0

Each version of Anaconda meeting this requirement will be downloaded from the `Continuum <http://continuum.io>`  archives, then checked to be sure that the size and md5 are correct.

============
Dependencies
============

* `beautifulsoup4 <http://www.crummy.com/software/BeautifulSoup/>`_
* `termcolor <https://pypi.python.org/pypi/termcolor>`_

====
TODO
====

Add a progress bar for downloads.

Automated license checking.

