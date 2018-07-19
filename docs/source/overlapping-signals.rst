.. only:: prerelease

    .. warning:: This is the documentation for a development version of flagman.

        .. only:: readthedocs

             `Documentation for the Most Recent Stable Version <http://flagman.readthedocs.io/en/stable/>`_

.. _overlapping-signals:

Overlapping Signals
===================

:program:`flagman` attempts to handle overlapping signals in an intelligent manner.
A signal is "overlapping" if it arrives while actions for previously-arrived signals
are still running.

:program:`flagman` handles overlapping signals of the same identity by coalescing and of
different identities by handling them serially but in a non-guaranteed order.

For example, take the following sequence of events.

#. :program:`flagman` is sleeping awaiting a signal to arrive
#. :code:`SIGUSR1` arrives
#. a long-running action for :code:`SIGUSR1` starts
#. :code:`SIGUSR2` arrives
#. the long-running action for :code:`SIGUSR1` finishes
#. a long-running action for :code:`SIGUSR2` starts
#. :code:`SIGUSR1` arrives
#. :code:`SIGUSR2` arrives; it is ignored since the :code:`SIGUSR2` actions are
   currently running
#. :code:`SIGHUP` arrives
#. the long-running action for :code:`SIGUSR2` finishes
#. a short-running action for :code:`SIGUSR2` starts and finishes
#. a short-running action for :code:`SIGHUP` starts and finishes; note that
   :code:`SIGHUP` arrived after the most recent :code:`SIGUSR1`--
   only intra-signal action ordering is guaranteed
#. a long-running action for :code:`SIGUSR1` starts
#. the long-running action for :code:`SIGUSR1` finishes
#. :program:`flagman` returns to sleep until the next handled signal arrives

