# -*- coding: utf-8 -*-
"""
emaillib package

Imports all parts from emaillib here
"""
from ._version import __version__
from emaillib import SmtpServer, EasySender, Message

__author__ = '''Costas Tyfoxylos'''
__email__ = '''costas.tyf@gmail.com'''

# This is to 'use' the module(s), so lint doesn't complain
assert __version__
assert __author__
assert __email__


# assert objects
assert SmtpServer
assert EasySender
assert Message
