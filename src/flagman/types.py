# -*- coding: utf-8 -*-
"""Type aliases used throughout flagman."""
from typing import Callable, Generator

ActionGenerator = Generator[None, None, None]
ActionGeneratorFunction = Callable[
    ..., ActionGenerator
]  # type: ignore (explicit "Any")
ActionName = str
ActionArgument = str
SignalNumber = int
