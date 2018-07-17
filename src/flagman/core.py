# -*- coding: utf-8 -*-
"""The core of flagman.

Contains the logic to implement signal handlers and dispatch to user-defined functions.
"""
import logging
import signal
from types import FrameType
from typing import (
    Iterable,
    List,
    Mapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Type,
    Union,
)

import pkg_resources

from flagman.actions import Action
from flagman.types import ActionArgument, ActionName, SignalNumber

logger = logging.getLogger(__name__)

#: Signals in this list are handled by flagman.
#: The CLI module auto-generates the appropriate CLI option for each signal.
HANDLED_SIGNALS: List[signal.Signals] = [signal.SIGUSR1, signal.SIGUSR2, signal.SIGHUP]

#: The global flag set for raised signals.
#: A signal that has been delivered to a handler will have its number in the set.
#: The number is removed after the actions for the signal have been executed.
SIGNAL_FLAGS: MutableSet[SignalNumber] = set()

#: Mapping of action entry point names to Action classes.
#: Populated from the pkg_resources `flagman.action` entry point group.
KNOWN_ACTIONS: Mapping[ActionName, Type[Action]] = {
    action.name: action.load()
    for action in pkg_resources.iter_entry_points('flagman.action')
}

#: Mapping of SignalNumbers to sequences of instantiated Actions ("action bundles")
#: that will be executed for that signal.
#: Populated by `create_action_bundles`.
ACTION_BUNDLES: Mapping[SignalNumber, MutableSequence[Action]] = {
    signum.value: [] for signum in HANDLED_SIGNALS
}


def create_action_bundles(
    args_dict: Mapping[str, Iterable[Sequence[Union[ActionName, ActionArgument]]]]
) -> int:
    """Parse the enabled actions and insert them into the global ACTION_BUNDLES mapping.

    The input dictionary should be like
    `{'usr1': [['action1', 'arg1a', 'arg2a'], ['action2', 'arg2a']],
     'usr2': [['action3'], ['action4', 'arg4a', 'arg4b']]}`.


    :param args_dict: a mapping of strings to an Iterable of Action names
    :returns: The number of configured actions
    """
    logger.debug('Creating action bundles')
    for signum in HANDLED_SIGNALS:
        logger.debug('Creating action bundle for %s', signum.name)
        action_calls = args_dict.get(signum.name[3:].lower(), [])
        actions = []
        for action_call in action_calls:
            try:
                actions.append((KNOWN_ACTIONS[action_call[0]], action_call[1:]))
            except KeyError:
                logger.error('Unknown action `%s`; skipping', action_call[0])
        action_generators = [
            prime_action_generator(action[0], action[1]) for action in actions
        ]
        ACTION_BUNDLES[signum.value].extend(action_generators)

    return sum(len(bundle) for bundle in ACTION_BUNDLES.values())


def prime_action_generator(
    action: Type[Action], args: Iterable[ActionArgument]
) -> Action:
    """Instantiate an Action.

    Given a class of type Action, instantiate the class with the passed-in arguments.

    :param action: the Action
    :param args: an Iterable of strings, the aruments to the Action

    :returns: the primed Action
    """
    logger.debug(
        'Priming action class `%s.%s` with arguments `%s`',
        action.__module__,
        action.__qualname__,
        args,
    )
    # instantiate the generator and run set up code
    action_generator = action(*args)

    return action_generator


def set_handlers() -> None:
    """Register handlers for the signals we're interested in.

    Uses the global HANDLED_SIGNALS to decide what signals to register for.

    Danger starts here!
    """
    logger.info('Registering signal handlers for actions')
    for signum in HANDLED_SIGNALS:
        if len(ACTION_BUNDLES[signum]) > 0:

            def handler(
                num: int, frame: FrameType
            ) -> None:  # noqa: D403 (capitalization)
                """flagman handler for {}.""".format(signum.name)
                SIGNAL_FLAGS.add(num)

            logger.debug('Registering signal handler for signal `%s`', signum.name)
            signal.signal(signum, handler)
        else:
            logger.debug(
                'No actions registered for signal `%s`; skipping handler registration',
                signum.name,
            )
    logger.info('Done registering signal handlers for actions')


def run() -> None:
    """Run the flagman "event loop".

    Waits for a signal to be raised and dispatches to the user-defined handlers
    as appropriate.
    """
    logger.info('Starting event loop')
    while True:
        logger.debug('Pausing for signal')
        signal.pause()
        logger.debug('Woke for signal')
        while SIGNAL_FLAGS:
            try:
                num = SIGNAL_FLAGS.pop()
                logger.debug('Found raised flag for signal number `%d`', num)
            except KeyError:
                continue

            actions_to_take = []
            for action_generator in ACTION_BUNDLES[num]:
                actions_to_take.append(action_generator)

            logger.debug(
                'Taking actions `%s` for signal number `%d`',
                [action.__class__.__name__ for action in actions_to_take],
                num,
            )
            for action in actions_to_take:
                logger.debug(
                    'Taking action `%s` for signal number `%d`',
                    action.__class__.__name__,
                    num,
                )
                next(action)
                logger.debug(
                    'Done taking action `%s` for signal number `%d`',
                    action.__class__.__name__,
                    num,
                )

            logger.debug('Lowering flag for signal number `%d`', num)
            SIGNAL_FLAGS.discard(num)
