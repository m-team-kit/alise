.. _development:

Development
===========

Repository
----------

Clone the repository to start developing:

.. code-block:: bash

   git clone https://github.com/marcvs/alise
   cd ./alise

Tox
---
We use tox to run the tests for supported python versions, lint the code using pylint and build this beautiful documentation:


.. code-block:: bash

   tox              # Do everything (recommended: use e.g. `-p 8` to run in parallel)
   tox -e docs      # Only build the docs
   tox -e pylint    # Only lint the code
   tox -e pyright   # Do static type checking using pyright
   tox -e py310     # Run a test for a specific python version


Code conventions
----------------
We use `pyright <https://github.com/microsoft/pyright>`_ for static type checking. Code is formatted using `black <https://github.com/psf/black>`_.


Releasing to PyPI
-----------------
To build a new version use:

.. code-block:: bash

    git tag <new version>   # Tag the release version
    git push                # Push the tag

    make dist               # build the release
    make upload             # upload it to PyPI (needs a valid PyPI account configured in ~/.pypirc)


*Read the Docs* will automatically update the documentation for the git tag.
