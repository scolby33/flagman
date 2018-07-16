# -*- coding: utf-8 -*-
"""Systemd notification protocol implementation."""
__license__ = """The MIT License (MIT)

Copyright (c) 2016 Brett Bethke
Modifications Copyrignt (c) 2018 Scott Colby

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import socket
import sys
from typing import Optional

__version__ = '0.3.2'

# Byte conversion utility for compatibility between
# Python 2 and 3.
# http://python3porting.com/problems.html#nicer-solutions
if sys.version_info < (3,):

    def _b(x):
        return x


else:

    def _b(x: str) -> bytes:
        return x.encode('latin-1')


class SystemdNotifier:
    """This class holds a connection to the systemd notification socket.

    It can be used to send messages to systemd using its notify method.
    """

    def __init__(self, debug: bool = False) -> None:
        """Instantiate a new notifier object.

        This will initiate a connection to the systemd notification socket.

        Normally this method silently ignores exceptions (for example, if the
        systemd notification socket is not available) to allow applications to
        function on non-systemd based systems. However, setting debug=True will
        cause this method to raise any exceptions generated to the caller, to
        aid in debugging.
        """
        self.debug = debug

        try:
            self.socket: Optional[socket.socket] = socket.socket(
                socket.AF_UNIX, socket.SOCK_DGRAM
            )
            addr = os.getenv('NOTIFY_SOCKET')
            assert addr is not None  # noqa: S101 (assert)
            if addr[0] == '@':
                addr = '\0' + addr[1:]
            self.socket.connect(addr)
        except:  # noqa: E722 (bare except)
            self.socket = None
            if self.debug:
                raise

    def notify(self, state: str) -> None:
        """Send a notification to systemd.

        State is a string; see the man page of sd_notify
        (http://www.freedesktop.org/software/systemd/man/sd_notify.html)
        for a description of the allowable values.

        Normally this method silently ignores exceptions (for example, if the
        systemd notification socket is not available) to allow applications to
        function on non-systemd based systems. However, setting debug=True will
        cause this method to raise any exceptions generated to the caller, to
        aid in debugging.
        """
        try:
            assert self.socket is not None  # noqa: S101 (assert)
            self.socket.sendall(_b(state))
        except:  # noqa: E722
            if self.debug:
                raise
