.. only:: prerelease

    .. warning:: This is the documentation for a development version of flagman.

        .. only:: readthedocs

             `Documentation for the Most Recent Stable Version <http://flagman.readthedocs.io/en/stable/>`_

.. _api:

API Reference
=============

.. module:: flagman

This part of the documentation covers all of the interfaces exposed by :mod:`flagman`.


The Action Class
----------------

This class is the abstract class you should inherit from to write your own actions.

.. autoclass:: Action
    :members:

    .. automethod:: _close


The Core Module
---------------

These functions and members are imported from the :mod:`flagman.core` module to be used
if using :mod:`flagman` as a library instead of a standalone tool.

.. data:: HANDLED_SIGNALS
    :annotation: List[signal.Signals]

    Signals in this list are handled by flagman.
    The CLI module auto-generates the appropriate CLI option for each signal.

.. data:: KNOWN_ACTIONS
    :annotation: Mapping[ActionName, Type[Action]]

    Mapping of action entry point names to Action classes.
    Populated from the pkg_resources `flagman.action` entry point group.

.. autofunction:: create_action_bundles

.. autofunction:: run

.. autofunction:: set_handlers


Errors and Exceptions
---------------------

.. autoexception:: ActionClosed


Built-in Actions
----------------

Print Actions
^^^^^^^^^^^^^

.. automodule:: flagman.actions.print

    .. autoclass:: flagman.actions.PrintAction
        :members:
        :show-inheritance:

    .. autoclass:: flagman.actions.DelayedPrintAction
        :members:
        :show-inheritance:

    .. autoclass:: flagman.actions.PrintOnceAction
        :members:
        :show-inheritance:

Types
-----

.. automodule:: flagman.types

    .. data:: ActionName

        Type alias for the name of an Action.

        alias of :class:`builtins.str`

    .. data:: ActionArgument

        Type alias for the the argument to an Action.

        alias of :class:`builtins.str`

    .. data:: SignalNumber

        Type alias for a signal number.

        alias of :class:`builtins.int`

The CLI Module
--------------

.. automodule:: flagman.cli
    :members:
    :private-members:


Systemd Notify Utilities
------------------------

.. automodule:: flagman.sd_notify

    .. autoclass:: SystemdNotifier
        :members:
        :private-members:
        :special-members: __init__
