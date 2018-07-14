# -*- coding: utf-8 -*-
from time import sleep

from flagman.types import ActionGenerator


def print_action() -> ActionGenerator:
    """during setup, print 'doing setup', when signaled, print 'called' and block for 10 seconds, then print 'done'"""
    try:
        print('doing setup')
        yield
        while True:
            print('called')
            sleep(10)
            print('done')
            yield
    except GeneratorExit:
        print('cleanup')


def print_action2() -> ActionGenerator:
    """during setup, print 'setup 2', when signaled, print 'called 2' and sleep for 2 seconds, then print 'done 2'"""
    try:
        print('setup 2')
        yield
        while True:
            print('called 2')
            sleep(2)
            print('done 2')
            yield
    except GeneratorExit:
        print('cleanup 2')
