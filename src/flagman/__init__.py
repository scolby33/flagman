# -*- coding: utf-8 -*-
"""Perform arbitrary actions on signals."""
from flagman import actions
from flagman import types
from flagman.actions import Action
from flagman.core import (
    HANDLED_SIGNALS,
    KNOWN_ACTIONS,
    create_action_bundles,
    run,
    set_handlers,
)
from flagman.exceptions import ActionClosed

__all__ = [
    'Action',
    'ActionClosed',
    'create_action_bundles',
    'set_handlers',
    'run',
    'HANDLED_SIGNALS',
    'KNOWN_ACTIONS',
    'actions',
    'types',
]
