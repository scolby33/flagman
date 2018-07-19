.. only:: prerelease

    .. warning:: This is the documentation for a development version of flagman.

        .. only:: readthedocs

             `Documentation for the Most Recent Stable Version <http://flagman.readthedocs.io/en/stable/>`_

.. _cli:

CLI Reference
=============

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

