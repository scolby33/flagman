.. flagman documentation master file, created by
   sphinx-quickstart on Wed Jul 18 17:18:26 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: <isonum.txt>

.. only:: prerelease

    .. warning:: This is the documentation for a development version of flagman.

        .. only:: readthedocs

             `Documentation for the Most Recent Stable Version <http://flagman.readthedocs.io/en/stable/>`_

Welcome to flagman!
===================

|python_versions| |license| |develop_build| |develop_coverage|

Perform arbitrary actions on signals.

.. |python_versions| image:: https://img.shields.io/badge/python-3.7-blue.svg?style=flat-square
    :target: https://www.youtube.com/watch?v=p33CVV29OG8&t=59m30s
    :alt: Supports Python 3.7
.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: LICENSE.rst
    :alt: MIT License
.. |develop_build| image:: https://img.shields.io/travis/com/scolby33/flagman/develop.svg?style=flat-square
    :target: https://travis-ci.com/scolby33/flagman
    :alt: Development Build Status
.. |develop_coverage| image:: https://img.shields.io/codecov/c/github/scolby33/flagman/develop.svg?style=flat-square
    :target: https://codecov.io/gh/scolby33/flagman/branch/develop
    :alt: Development Test Coverage Status

.. TODO fix Travis shield when shields.io does a release

.. code-block:: sh

    $ flagman --usr1 print 'a fun message' --usr1 print 'another message' --usr2 print_once 'will be printed once' &
    INFO:flagman.cli:PID: 49220
    INFO:flagman.cli:Setting loglevel to WARNING
    init  # the set_up phase of the three actions
    init
    init
    $ kill -usr1 49220  # actions are called in the order they're passed in the arguments
    a fun message
    another message
    $ kill -usr2 49220  # actions can remove themselves when no longer useful
    will be printed once
    cleanup  # the tear_down phase of the `print_once` action
    WARNING:flagman.core:Received `ActionClosed`; removing action `PrintOnceAction`
    # *snip* traceback
    flagman.exceptions.ActionClosed: Only print once
    $ kill -usr1 49220  # other actions are still here, though
    a fun message
    another message
    $ kill 49220  # responds gracefully to shutdown requests
    cleanup  # the tear_down phase of the two remaining actions
    cleanup


On this page:

.. contents::
    :local:

Features
--------

- Safe execution of code upon receiving
  :code:`SIGHUP`, :code:`SIGUSR1`, or :code:`SIGUSR2`
- Optional systemd integration--sends :code:`READY=1` message when startup is complete
- Complete `mypy <http://mypy-lang.org/>`_ type annotations

Use Cases
---------

The use cases are endless!
But specifically, :mod:`flagman` is useful to adapt services that do not handle
signals in a convenient way for your infrastructure.

I wrote :mod:`flagman` to solve a specific problem, examined in
:ref:`real-world`.

The Anatomy of an Action
------------------------

Learn how to create your own Actions!

.. toctree::
    :maxdepth: 2

    action-anatomy


Overlapping Signals
-------------------

:mod:`flagman` attempts to handle overlapping signals in an intelligent manner.
This algorithm is explained here:

.. toctree::
    :maxdepth: 2

    overlapping-signals


A Real-World Use
----------------

An examination of the problem I built :mod:`flagman` to solve.

.. toctree::
    :maxdepth: 2

    real-world


CLI Reference
-------------

The CLI options for :program:`flagman` are documented here.

.. toctree::
    :maxdepth: 2

    cli


API Reference
-------------

Information about the interfaces :mod:`flagman` exposes are here.

.. toctree::
    :maxdepth: 2

    api


Installation
------------

:mod:`flagman` has no required dependencies outside the Python Standard Library.

At the moment, installation must be performed via GitHub:

.. code-block:: sh

    $ pip install git+https://github.com/scolby33/flagman.git

For prettier output for :code:`flagman --list`, install the :code:`color` extra:

.. code-block:: sh

    $ pip install git+https://github.com/scolby33/flagman.git[color]

:mod:`flagman` targets Python 3 and tests with Python 3.7.
Versions earlier than 3.7 are not guaranteed to work.


Changelog
---------

:mod:`flagman` adheres to the Semantic Versioning ("Semver") 2.0.0 versioning standard.
Details about this versioning scheme can be found on the `Semver website <http://semver.org/spec/v2.0.0.html>`_.
Versions postfixed with '-dev' are currently under development and those without a
postfix are stable releases.

You are reading the documents for version |release| of :mod:`flagman`.

Changes as of 18 July 2018

- Initial implementation of the flagman functionality.


Contributing
------------

There are many ways to contribute to an open-source project,
but the two most common are reporting bugs and contributing code.

If you have a bug or issue to report, please visit the
`issues page on GitHub <https://github.com/scolby33/flagman/issues>`_ and open an issue there.

If you want to make a code contribution, feel free to open a pull request!


License
-------

The systemd notification portion of flagman is originally
Copyright |copy| 2016 Brett Bethke and is provided under the MIT license.
The original source is found at https://github.com/bb4242/sdnotify.

The remainder of flagman is Copyright |copy| 2018 Scott Colby and is available
under the MIT license.

See the `LICENSE.rst <https://github.com/scolby33/flagman/blob/develop/LICENSE.rst>`_
file in the root of the source code repository for the full text of the license.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
