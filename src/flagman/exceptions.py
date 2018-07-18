# -*- coding: utf-8 -*-
"""Exceptions for flagman."""


class ActionClosed(Exception):
    """The Action is closed and no longer will do anything on a call to `run()`."""

    pass
