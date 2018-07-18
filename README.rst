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


.. contents:: :local:


Features
--------

- Safe execution of code upon receiving
  :code:`SIGHUP`, :code:`SIGUSR1`, or :code:`SIGUSR2`
- Optional systemd integration--sends :code:`READY=1` message when startup is complete
- Complete `mypy <http://mypy-lang.org/>`_ type annotations


Use Cases
---------

The use cases are endless!
But specifically, :code:`flagman` is useful to adapt services that do not handle
signals in a convenient way for your infrastructure.

I wrote :code:`flagman` to solve a specific problem, examined in
`A Real-World Use`_ below.

The Anatomy of an Action
------------------------

Actions are the primary workhorse of :code:`flagman`.
Writing your own actions allows for infinite possible uses of the tool!

The Action Class
^^^^^^^^^^^^^^^^

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
    name  - description [(argument: type, ...)]
    --------------------------------------------------------------------------------
    print - A simple Action that prints messages at the various stages of execution.
            (message: str)


If the :code:`Action` takes arguments, it is wise to document them here.
The name of the action is defined in an entry point--see `Registering an Action`_ below.

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

Because of :code:`flagman`'s architecture, it is safe to do *anything* inside the
:code:`run()` method.
It is not actually called from the signal handler, but in the main execution loop
of the program.
Therefore, normally "risky" things to do in signal handlers involving locks, etc.
(including using the :code:`logging` module, for example) are completely safe.

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

Registering an Action
^^^^^^^^^^^^^^^^^^^^^

:code:`flagman` detects available actions in the :code:`flagman.action` entry point
group.
Actions must be distributed in packages with this entry point defined.
For instance, here is how the built-in actions are referenced in :code:`flagman`'s
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


A Real-World Use
----------------

I have a multi-layered DNS setup that involves ALIAS records that are only resolved on
a hidden master and are passed as A or AAAA records to the authoritative slaves.

I wanted to check if the resolved value of the ALIAS records have changed and send out
DNS NOTIFYs to the slaves when they do, but I didn't want to store state in a file
on disk.

Enter :code:`flagman`. I wrote an action that queries the hidden master and saves the
values of the records I'm interested in as member variables. If the values have changed
since the last run, the hidden master's REST API is called for force the sending of a
NOTIFY out to its slaves.

This is integrated with three systemd units:

.. code-block:: ini

    # flagman.service
    [Unit]
    Description=Run flagman

    [Service]
    Type=notify
    NotifyAccess=main
    ExecStart=/path/to/flagman --usr1 dnscheck

.. code-block:: ini

    # flagman-notify.service
    [Unit]
    Description=Send SIGUSR1 to flagman

    [Service]
    Type=oneshot
    ExecStart=/bin/systemctl kill -s SIGUSR1 flagman.service

.. code-block:: ini

    # flagman-notify.timer
    [Unit]
    Description=Run flagman-notify hourly

    [Timer]
    OnCalendar=hourly
    RandomizedDelaySec=300
    Persistent=true

    [Install]
    WantedBy=timers.target


Simple? Not quite. But quite extensible and useful in a variety of situations.



CLI Reference
-------------

-h, --help            show this help message and exit
--list, -l            list known actions and exit
--hup ACTION          add an action for SIGHUP
--usr1 ACTION         add an action for SIGUSR1
--usr2 ACTION         add an action for SIGUSR2
--successful-empty    if all actions are removed, exit with 0 instead of the default 1
--no-systemd          do not notify systemd about status
--quiet, -q           only output critial messages; overrides `--verbose`
--verbose, -v         increase the loglevel; pass multiple times for more verbosity

Notes
^^^^^

- Options to add actions take the argument *ACTION*, the action name as shown in
  :code:`flagman --list`, followed by an action-defined number of arguments, which are
  also documented in :code:`flagman --list`.
  See the output of :code:`flagman --help` for a more complete view of this.
- All options to add actions for signals may be passed multiple times.
- When a signal with multiple actions is handled, the actions are guaranteed to
  be taken in the order they were passed on the command line.
- Calling with no actions set is a critical error and will cause an immediate
  exit with code 2.

Installation
------------
:code:`flagman` has no required dependencies outside the Python Standard Library.

At the moment, installation must be performed via GitHub:

.. code-block:: sh

    $ pip install git+https://github.com/scolby33/flagman.git

For prettier output for :code:`flagman --list`, install the :code:`color` extra:

.. code-block:: sh

    $ pip install git+https://github.com/scolby33/flagman.git[color]

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
