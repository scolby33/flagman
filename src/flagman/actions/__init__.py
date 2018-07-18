# -*- coding: utf-8 -*-
"""Built-in flagman actions.

These simple actions are probably only useful for debugging.
"""
from flagman.actions.action import Action
from flagman.actions.print import DelayedPrintAction, PrintAction, PrintOnceAction

__all__ = ['Action', 'PrintAction', 'DelayedPrintAction', 'PrintOnceAction']
