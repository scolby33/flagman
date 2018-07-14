# -*- coding: utf-8 -*-
from typing import Callable, Generator

ActionGenerator = Generator[None, None, None]
ActionGeneratorFunction = Callable[[], ActionGenerator]
ActionName = str
SignalNumber = int
