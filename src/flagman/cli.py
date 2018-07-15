#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module that contains the command line for flagman.

Why does this file exist, and why not put this in __main__?
You might be tempted to import things from __main__ later, but that will cause
problems--the code will get executed twice:
  - When you run `python -m flagman` python will execute
    `__main__.py` as a script. That means there won't be any
    `flagman.__main__` in `sys.modules`.
  - When you import __main__ it will get executed again (as a module)
    because there's no `flagman.__main__` in `sys.modules`.
Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import os
import sys
import textwrap
from typing import Optional, Sequence

from colorama import init as colorama_init
from colorama import Style

from flagman import (
    HANDLED_SIGNALS,
    KNOWN_ACTIONS,
    create_action_bundles,
    run,
    set_handlers,
)

EPILOG_TEXT = """NOTES:
 - All options to add actions for signals may be passed multiple times.
 - When a signal with multiple actions is handled, the actions are guaranteed to
   be taken in the order they were passed on the command line.
 - Calling with no actions set is an error and will cause an immediate exit."""


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse the arguments for the flagman CLI.

    :param argv: a Squence of argument strings

    :returns: the parsed arguments as an argparse Namespace
    """
    parser = argparse.ArgumentParser(
        prog='flagman',
        description='Perform arbitrary actions on signals.',
        epilog=EPILOG_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '--list', '-l', action='store_true', help='list known actions and exit'
    )
    for signum in HANDLED_SIGNALS:
        name = signum.name
        parser.add_argument(
            '--{}'.format(name[3:].lower()),
            action='append',
            nargs='+',
            default=[],
            # TODO: custom choices container
            # choices=KNOWN_ACTIONS.keys(),
            help='add an action for {}'.format(name),
            metavar=('ACTION', 'ARGUMENT'),
        )
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help="don't output anything; overrides `--verbose`",
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='count',
        default=0,
        help='increase the loglevel; pass multiple times for more verbosity',
    )

    return parser.parse_args(argv[1:])


def main() -> Optional[int]:  # noqa: D401 (First line should be in imperative mood)
    """The main function of the flagman CLI.

    Don't call this from library code, use your own version implenting analogous logic.

    :returns: An exit code or None
    """
    args = parse_args(sys.argv)
    if args.list:
        colorama_init(autoreset=True)
        max_action_name_len = max(len(name) for name in KNOWN_ACTIONS.keys())
        wrapper = textwrap.TextWrapper(
            width=80 - max_action_name_len - 3,
            subsequent_indent=' ' * (max_action_name_len + 3),
        )
        for name, action in KNOWN_ACTIONS.items():
            wrapped_doc = wrapper.fill(str(action.__doc__))
            print(
                '{bright}{name:<{max_action_name_len}} -{normal} {doc}'.format(
                    bright=Style.BRIGHT,
                    name=name,
                    max_action_name_len=max_action_name_len,
                    normal=Style.NORMAL,
                    doc=wrapped_doc,
                )
            )
        return None

    print('PID: {}'.format(os.getpid()), flush=True)

    args_dict = vars(args)
    create_action_bundles(args_dict)
    set_handlers()
    run()
    return None


if __name__ == '__main__':
    sys.exit(main())
