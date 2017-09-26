
This repository is intended for tracking releases of the LAT extended source archive.


Making Changes to the Archive
-----------------------------

To add a new extended source or make changes to an existing source:

* Make a fork of this repository.
* Clone your forked repository.
* Make changes by editing ``master.yaml`` and/or adding new FITS templates to the Templates directory.
* Commit your changes to your forked repo and open a Pull Request to this repository with these changes.

Building the Archive
--------------------

.. code-block:: bash

   $ python build_archive.py master.yaml --output=LAT_extended_sources_vXX
  

Creating a new Release
----------------------

To make a new release of the archive, checkout the current master branch and tag the repo with:

.. code-block:: bash

   $ git tag vXX

wher vXX is the extended archive release number.
