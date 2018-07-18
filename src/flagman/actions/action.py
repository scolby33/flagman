# -*- coding: utf-8 -*-
"""The base Action class for all other Actions to inherit from."""
from abc import ABCMeta, abstractmethod

from flagman.exceptions import ActionClosed


class Action(metaclass=ABCMeta):
    """The base Action class."""

    def __init__(self, *args: str) -> None:
        """Instantiate the ActionGenerator and run the set up code.

        :param args: arguments that will be passed to the set_up method
        """
        self._closed = False
        self.set_up(*args)

    def _run(self) -> None:
        """Run the action if it hasn't been closed."""
        if not self._closed:
            self.run()
        else:
            raise ActionClosed

    def _close(self) -> None:
        """Close the action, preventing future runs and executing tear down logic."""
        if not self._closed:
            self._closed = True
            self.tear_down()

    def __del__(self) -> None:
        """Close the generator at destruction time."""
        self._close()

    def set_up(self, *args: str) -> None:
        """Perform any required set up for the Action."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Run the Action."""
        pass

    def tear_down(self) -> None:
        """Perform any required clean up for the Action."""
        pass
