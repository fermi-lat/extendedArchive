
This repository contains tools and data files for generating releases of the LAT extended source archive.


Proposing Changes to the Archive
--------------------------------

To add a new extended source or make changes to an existing source:

* Make a fork of this repository.
* Clone your forked repository.
* Make changes by editing ``archive.yaml`` and/or adding new FITS templates to the Templates directory.
* Commit your changes to your forked repo and open a Pull Request to this repository with these changes.

To add a source create a new block in ``archive.yaml`` with key equal
to the source name.  To update a source edit its properties in
``archive.yaml``.  If a FITS template has changed create a new unique
template file in the ``Templates`` directory.

  
Building the Archive
--------------------

The ``build_archive.py`` script constructs the archive directory
structure from the master archive YAML file.  The ``--output`` option
sets the path to the extended archive directory root directory.

.. code-block:: bash

   $ python build_archive.py archive.yaml --outdir=Extended_archive_vXX
  

Creating a new Release
----------------------

To make a new release of the archive, checkout the current master branch and tag the repo with:

.. code-block:: bash

   $ git tag vXX

where vXX is the extended archive release number.
