.. only:: prerelease

    .. warning:: This is the documentation for a development version of flagman.

        .. only:: readthedocs

             `Documentation for the Most Recent Stable Version <http://flagman.readthedocs.io/en/stable/>`_

.. _action-anatomy:

The Anatomy of an Action
========================

Actions are the primary workhorse of :mod:`flagman`.
Writing your own actions allows for infinite possible uses of the tool!

The Action Class
----------------

Actions are instances of the abstract base class :class:`flagman.Action`.
Let's look at the included :class:`PrintAction` as an illustrative example.

.. code-block:: python

    class PrintAction(Action):
        """A simple Action that prints messages at the various stages of execution.

        (message: str)
        """

        def set_up(self, msg: str) -> None:  # type: ignore
            """Store the message to be printed and print the "init" message.

            :param msg: the message
            """
            self_msg = msg
            print('init')

        def run(self) -> None:
            """Print the message."""
            print(self._msg)

        def tear_down(self) -> None:
            """Print "cleanup" message."""
            print('cleanup')


We start with a standard class definition and docstring:

.. code-block:: python

    class PrintAction(Action):
        """A simple Action that prints messages at the various stages of execution.

        (message: str)
        """

We inherit from :class:`Action`.
The docstring is parsed and becomes the documentation for the action in the CLI output:

.. code-block:: sh

    $ flagman --list
    name  - description [(argument: type, ...)]
    --------------------------------------------------------------------------------
    print - A simple Action that prints messages at the various stages of execution.
            (message: str)


If the :class:`Action` takes arguments, it is wise to document them here.
The name of the action is defined in an entry point--see `Registering an Action`_ below.

Next is the :meth:`set_up()` method.

.. code-block:: python

        def set_up(self, msg: str) -> None:  # type: ignore
            """Store the message to be printed and print the "init" message.

            :param msg: the message
            """
            self_msg = msg
            print('init')

All arguments will be passed to this method as strings. If other types are expected,
do the conversion in :meth:`set_up()` and raise errors as necessary.
If `mypy <http://mypy-lang.org/>`_ is being used, the :code:`# type: ignore`
comment is required since the parent implementation takes :code:`*args`.

Do any required set up in this method: parsing arguments, reading external data, etc.
If you want values from the environment
(e.g. if API tokens or other values that should not be passed on the command line are
needed), you can get them here.
:mod:`flagman` itself does not provide facilities for parsing the environment,
configuration files, etc.

Next we have the most important method, :meth:`run()`. This is the only abstract method
on :class:`Action` and as such it must be implemented.

.. code-block:: python

        def run(self) -> None:
            """Print the message."""
            print(self._msg)

Perform whatever action you wish here.
This method is called once for each time :program:`flagman` is signaled with the proper
signal, assuming low enough rates of incoming signals.
See below in the :ref:`overlapping-signals` section for more information.

Because of :mod:`flagman`'s architecture, it is safe to do *anything* inside the
:meth:`run()` method.
It is not actually called from the signal handler, but in the main execution loop
of the program.
Therefore, normally "risky" things to do in signal handlers involving locks, etc.
(including using the :mod:`logging` module, for example) are completely safe.

Finally, there is the :meth:`tear_down()` method.

.. code-block:: python

        def tear_down(self) -> None:
            """Print "cleanup" message."""
            print('cleanup')

Here you can perform any needed cleanup for your action like closing connections,
writing out statistics, etc.

This method will be called when the action is "closed" (see below),
during garbage collection of the action, and before :mod:`flagman` shuts down.

"Closing" an Action
-------------------

If an Action has fulfilled its purpose or otherwise no longer needs to be called,
it can be "closed" by calling its :meth:`_close()` method.
This method takes no arguments and always returns :code:`None`.

Calling this method does two things: it calls the action's :meth:`tear_down()` method
and it sets a flag that prevents further calls to the internal :meth:`_run()` method
that :mod:`flagman` uses to actually run Actions.

Further calls to :meth:`_run()` will raise a :exc:`flagman.ActionClosed` exception
and will cause the removal of the action from the internal list of actions to be run.
If there are no longer any non-closed actions, :program:`flagman` will exit with
code :code:`1`, unless it was originally called with the :code:`--successful-empty`
option, in which case it will exit with :code:`0`.

If you want to close your own action in its :meth:`run()` method, a construction like
so is advised:

.. code-block:: python

    def run(self) -> None:
        if some_condition:
            self._close()
            raise ActionClosed('Closing because of some_condition')
        else:
            ...

This will print your argument to :exc:`ActionClosed` to the log and will result in the
immediate removal of the action from the list of actions to be run.
If :exc:`ActionClosed` is not raised, :program:`flagman` will not realize the action has
been closed and will not remove it from the list of actions to be run until the next
time :meth:`run()` would be called,
i.e. the next time the signal is delivered for the action.

Registering an Action
---------------------

:mod:`flagman` detects available actions in the :code:`flagman.action` entry point
group.
Actions must be distributed in packages with this entry point defined.
For instance, here is how the built-in actions are referenced in :mod:`flagman`'s
:code:`setup.cfg`:

.. code-block:: ini

    [options.entry_points]
    flagman.action =
        print = flagman.actions:PrintAction
        delay_print = flagman.actions:DelayedPrintAction
        print_once = flagman.actions:PrintOnceAction

The name to the left of the :code:`=` is how the action will be referenced in the CLI.
The entry point specifier to the right of the :code:`=` points to the class implementing
the action.
See `the Setuptools documentation <https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins>`_ for more information about using entry points.
