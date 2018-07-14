# -*- coding: utf-8 -*-
import signal
from types import FrameType
from typing import Iterable, List, Mapping, MutableSequence, MutableSet

import pkg_resources

from flagman.types import (
    ActionGenerator,
    ActionGeneratorFunction,
    ActionName,
    SignalNumber,
)

HANDLED_SIGNALS: List[signal.Signals] = [signal.SIGUSR1, signal.SIGUSR2, signal.SIGHUP]
SIGNAL_FLAGS: MutableSet[SignalNumber] = set()
KNOWN_ACTIONS: Mapping[ActionName, ActionGeneratorFunction] = {
    action.name: action.load()
    for action in pkg_resources.iter_entry_points('flagman.action')
}
ACTION_BUNDLES: Mapping[SignalNumber, MutableSequence[ActionGenerator]] = {
    signum.value: [] for signum in HANDLED_SIGNALS
}


def create_action_bundles(args_dict: Mapping[str, Iterable[ActionName]]) -> None:
    for signum in HANDLED_SIGNALS:
        action_names = args_dict.get(signum.name.lower()[3:], [])
        actions = [KNOWN_ACTIONS[action_name] for action_name in action_names]
        action_generators = [prime_action_generator(action) for action in actions]
        ACTION_BUNDLES[signum.value].extend(action_generators)


def prime_action_generator(action: ActionGeneratorFunction) -> ActionGenerator:
    # instantiate the generator
    action_generator = action()
    # run the setup code
    next(action_generator)

    return action_generator


def set_handlers() -> None:
    for signum in HANDLED_SIGNALS:

        def handler(num: int, frame: FrameType) -> None:
            """flagman handler for {}""".format(signum.name)
            SIGNAL_FLAGS.add(num)

        signal.signal(signum, handler)


def run() -> None:
    while True:
        signal.pause()
        while SIGNAL_FLAGS:
            try:
                num = SIGNAL_FLAGS.pop()
            except KeyError:
                continue

            actions_to_take = []
            for action_generator in ACTION_BUNDLES[num]:
                actions_to_take.append(action_generator)

            for action in actions_to_take:
                next(action)

            SIGNAL_FLAGS.discard(num)
