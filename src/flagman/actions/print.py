# -*- coding: utf-8 -*-
"""Print actions for flagman.

Most likely only useful for debugging.
"""
from time import sleep

from flagman.actions import Action
from flagman.exceptions import ActionClosed


class PrintAction(Action):
    """A simple Action that prints messages at the various stages of execution.

    (message: str)
    """

    def set_up(self, msg: str) -> None:  # type: ignore
        """Store the message to be printed and print "init" message.

        :param msg: the message
        """
        self._msg = msg
        print('init')

    def run(self) -> None:
        """Print the message."""
        print(self._msg)

    def tear_down(self) -> None:
        """Print "cleanup" message."""
        print('cleanup')


class DelayedPrintAction(PrintAction):
    """An Action that prints messages at the various stages of execution and has a configurable delay in the run stage.

    (message: str, delay: int)
    """  # noqa: E501

    def set_up(self, msg: str, delay: str) -> None:  # type: ignore
        """Store the message and the delay.

        :param msg: the message
        :param delay: the delay in seconds
        """
        self._delay = int(delay)
        super().set_up(msg)

    def run(self) -> None:
        """Print the message, delay, and print a finished message."""
        super().run()
        sleep(self._delay)
        print('finished delaying')


class PrintOnceAction(PrintAction):
    """An Action that prints a message once and then cleans up after itself.

    (message: str)
    """

    def set_up(self, msg: str) -> None:  # type: ignore
        """Store the message.

        :param msg: the message
        """
        super().set_up(msg)

    def run(self) -> None:
        """Print the message and close the action."""
        super().run()
        self._close()
        raise ActionClosed('Only print once')
