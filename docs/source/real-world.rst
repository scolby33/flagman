.. only:: prerelease

    .. warning:: This is the documentation for a development version of flagman.

        .. only:: readthedocs

             `Documentation for the Most Recent Stable Version <http://flagman.readthedocs.io/en/stable/>`_

.. _real-world:

A Real-World Use
================

I have a multi-layered DNS setup that involves ALIAS records that are only resolved on
a hidden master and are passed as A or AAAA records to the authoritative slaves.

I wanted to check if the resolved value of the ALIAS records have changed and send out
DNS NOTIFYs to the slaves when they do, but I didn't want to store state in a file
on disk.

Enter :mod:`flagman`. I wrote an action that queries the hidden master and saves the
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

