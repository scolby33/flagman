# -*- coding: utf-8 -*-
"""The base Action class for all other Actions to inherit from."""
from abc import ABCMeta, abstractmethod
from types import TracebackType
from typing import Any, Generator, Optional, Type


class Action(Generator[None, None, None], metaclass=ABCMeta):
    """The base Action class."""

    def __init__(self, *args: str) -> None:
        """Instantiate the ActionGenerator and run the set up code.

        :param args: arguments that will be passed to the set_up method
        :param kwargs: keyword arguments that will be passed to the set_up method
        """
        self._closed = False
        self.set_up(*args)

    def send(self, _: Optional[Any]) -> None:  # type: ignore
        """Send in an ignored value and execute the run method.

        :param _: ignored
        """
        if not self._closed:
            self.run()
        else:
            raise StopIteration

    def throw(
        self,
        typ: Type[BaseException],
        value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        """Throw an exception in the generator.

        If GeneratorExit is thrown, close the generator.

        :param typ: the exception to be thrown
        :param value: the value for the exception
        :param traceback: the traceback to attach to the exception
        """
        if typ is GeneratorExit and not self._closed:
            self._closed = True
            self.tear_down()
        super().throw(typ, value, traceback)

    def __del__(self) -> None:
        """Close the generator at destruction time."""
        self.close()

    def set_up(self, *args: str) -> None:
        """Perform any required set up for the Action."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Run the action."""
        pass

    def tear_down(self) -> None:
        """Perform any required clean up for the Action."""
        pass
