flagman |python_versions| |license| |develop_build| |develop_coverage|
=======================================================================
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


The Anatomy of an Action
------------------------

Actions are instances of the abstract base class :code:`flagman.Action`.
Let's look at the included :code:`PrintAction` as an illustrative example.

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

We inherit from :code:`Action`.
The docstring is parsed and becomes the documentation for the action in the CLI output:

.. code-block:: sh

    $ flagman --list
    name        - description [(argument: type, ...)]
    --------------------------------------------------------------------------------
    print       - A simple Action that prints messages at the various stages of
                  execution. (message: str)

If the :code:`Action` takes arguments, it is wise to document them here.

Next is the :code:`set_up()` method.

.. code-block:: python

        def set_up(self, msg: str) -> None:  # type: ignore
            """Store the message to be printed and print the "init" message.

            :param msg: the message
            """
            self_msg = msg
            print('init')

All arguments will be passed to this method as strings. If other types are expected,
do the conversion in :code:`set_up()` and raise errors as necessary.
If `mypy <http://mypy-lang.org/>`_ is being used, the :code:`# type: ignore`
comment is required since the parent implementation takes :code:`*args`.

Do any required set up in this method: parsing arguments, reading external data, etc.
If you want values from the environment
(e.g. if API tokens or other values that should not be passed on the command line are
needed), you can get them here.
:code:`flagman` itself does not provide facilities for parsing the environment,
configuration files, etc.

Next we have the most important method, :code:`run`. This is the only abstract method
on :code:`Action` and as such it must be implemented.

.. code-block:: python

        def run(self) -> None:
            """Print the message."""
            print(self._msg)

Perform whatever action you wish here.
This method is called once for each time :code:`flagman` is signaled with the proper
signal, assuming low enough rates of incoming signals.
See below in the `Overlapping Signals`_ section for more information.

Finally, there is the :code:`tear_down()` method.

.. code-block:: python

        def tear_down(self) -> None:
            """Print "cleanup" message."""
            print('cleanup')

Here you can perform any needed cleanup for your action like closing connections,
writing out statistics, etc.

This method will be called when the action is "closed" (see below),
during garbage collection of the action, and before :code:`flagman` shuts down.

"Closing" an Action
^^^^^^^^^^^^^^^^^^^

If an Action has fulfilled its purpose or otherwise no longer needs to be called,
it can be "closed" by calling its :code:`_close()` method.
This method takes no arguments and always returns :code:`None`.

Calling this method does two things: it calls the action's :code:`tear_down()` method
and it sets a flag that prevents further calls to the internal :code:`_run()` method
that :code:`flagman` uses to actually run Actions.

Further calls to :code:`_run()` will raise a :code:`flagman.ActionClosed` exception
and will cause the removal of the action from the internal list of actions to be run.
If there are no longer any non-closed actions, :code:`flagman` will exit with
code :code:`1`, unless it was originally called with the :code:`--successful-empty`
option, in which case it will exit with :code:`0`.

If you want to close your own action in its :code:`run()` method, a construction like
so is advised:

.. code-block:: python

    def run(self) -> None:
        if some_condition:
            self._close()
            raise ActionClosed('Closing because of some_condition')
        else:
            ...

This will print your argument to :code:`ActionClosed` to the log and will result in the
immediate removal of the action from the list of actions to be run.
If :code:`ActionClosed` is not raised, :code:`flagman` will not realize the action has
been closed and will not remove it from the list of actions to be run until the next
time :code:`run()` would be called,
i.e. the next time the signal is delivered for the action.


Overlapping Signals
-------------------

:code:`flagman` attempts to handle overlapping signals in an intelligent manner.
A signal is "overlapping" if it arrives while actions for previously-arrived signals
are still running.

:code:`flagman` handles overlapping signals of the same identity by coalescing and of
different identities by handling them serially but in a non-guaranteed order.

For example, take the following sequence of events.

#. :code:`flagman` is sleeping awaiting a signal to arrive
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
#. :code:`flagman` returns to sleep until the next handled signal arrives


Installation
------------
At the moment, installation must be performed via GitHub:

.. code-block:: sh

    $ pip install git+https://github.com/scolby33/flagman.git

:code:`flagman` targets Python 3 and tests with Python 3.7.
Versions earlier than 3.7 are not guaranteed to work.

Changelog
---------
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
Copyright (c) 2016 Brett Bethke and is provided under the MIT license.
The original source is found at https://github.com/bb4242/sdnotify.

The remainder of flagman is Copyright (c) 2018 Scott Colby and is available
under the MIT license.

See the `LICENSE.rst <LICENSE.rst>`_ file for the full text of the license.
