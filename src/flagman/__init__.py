# -*- coding: utf-8 -*-
"""Perform arbitrary actions on signals."""
from flagman import actions
from flagman import types
from flagman.core import (
    HANDLED_SIGNALS,
    KNOWN_ACTIONS,
    create_action_bundles,
    run,
    set_handlers,
)

__all__ = [
    'create_action_bundles',
    'set_handlers',
    'run',
    'HANDLED_SIGNALS',
    'KNOWN_ACTIONS',
    'actions',
    'types',
]
