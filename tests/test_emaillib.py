#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: test_emaillib.py
#
# Copyright 2017 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Tests for `emaillib` module.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

from betamax.fixtures import unittest
from emaillib.emaillib import Message, SmtpServer, EasySender

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''16-09-2017'''
__copyright__ = '''Copyright 2017, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


class TestEmaillib(unittest.BetamaxTestCase):

    def setUp(self):
        """
        Test set up

        This is where you can setup things that you use throughout the tests. This method is called before every test.
        """
        pass

    def testNoSender(self):
        info = {'sender': '',
                'recipients': 'whatever@gmail.com',
                'cc': ['somebody@gmail.com'],
                'bcc': 'more@gmail.com,andmore@gmail.com',
                'subject': 'Τεστ test',
                'body': 'This is a τεστ on utf8'}
        with self.assertRaises(ValueError):
            message = Message(**info)

    def testInvalidSender(self):
        invalid = ['a',
                   'a@',
                   '@.',
                   '@a.',
                   '.@',
                   'a@@',
                   'a@@.']
        for sender in invalid:
            info = {'sender': sender,
                    'recipients': 'whatever@gmail.com',
                    'subject': 'Τεστ test',
                    'body': 'This is a τεστ on utf8'}
            with self.assertRaises(ValueError):
                message = Message(**info)

    def testNoRecipient(self):
        info = {'sender': 'whatever@gmail.com',
                'recipients': '',
                'cc': ['somebody@gmail.com'],
                'bcc': 'more@gmail.com,andmore@gmail.com',
                'subject': 'Τεστ test',
                'body': 'This is a τεστ on utf8'}
        with self.assertRaises(ValueError):
            message = Message(**info)

    def testInvalidRecipient(self):
        invalid = ['a',
                   'a@',
                   '@.',
                   '@a.',
                   '.@',
                   'a@@',
                   'a@@.',
                   'a@a.com,a.',
                   'inv.domain.com,valid@test.com']
        for recipients in invalid:
            info = {'sender': 'whatever@gmail.com',
                    'recipients': recipients,
                    'subject': 'Τεστ test',
                    'body': 'This is a τεστ on utf8'}
            with self.assertRaises(ValueError):
                print(recipients)
                message = Message(**info)

    def testInvalidCC(self):
        invalid = ['a',
                   'a@',
                   '@.',
                   '@a.',
                   '.@',
                   'a@@',
                   'a@@.',
                   'a@a.com,a.',
                   'inv.domain.com,valid@test.com']
        for cc in invalid:
            info = {'sender': 'whatever@gmail.com',
                    'recipients': 'another@valid.com',
                    'cc': cc,
                    'subject': 'Τεστ test',
                    'body': 'This is a τεστ on utf8'}
            with self.assertRaises(ValueError):
                message = Message(**info)

    def testInvalidBCC(self):
        invalid = ['a',
                   'a@',
                   '@.',
                   '@a.',
                   '.@',
                   'a@@',
                   'a@@.',
                   'a@a.com,a.',
                   'inv.domain.com,valid@test.com']
        for bcc in invalid:
            info = {'sender': 'whatever@gmail.com',
                    'recipients': 'another@valid.com',
                    'bcc': bcc,
                    'subject': 'Τεστ test',
                    'body': 'This is a τεστ on utf8'}
            with self.assertRaises(ValueError):
                message = Message(**info)

    def testValid(self):
        info = {'sender': 'test@valid.com',
                'recipients': 'whatever@gmail.com',
                'cc': ['somebody@gmail.com'],
                'bcc': 'more@gmail.com,andmore@gmail.com',
                'subject': 'Τεστ test',
                'body': 'This is a τεστ on utf8'}
        message = Message(**info)
        self.assertTrue(message.subject == u'Τεστ test')
        self.assertTrue(message.body == u'This is a τεστ on utf8')

    def testInvalidContent(self):
        info = {'sender': '',
                'recipients': 'whatever@gmail.com',
                'cc': ['somebody@gmail.com'],
                'bcc': 'more@gmail.com,andmore@gmail.com',
                'subject': 'Τεστ test',
                'body': 'This is a τεστ on utf8',
                'content': 'Texd'}
        with self.assertRaises(ValueError):
            message = Message(**info)

    def testHtmlContent(self):
        info = {'sender': 'test@test.com',
                'recipients': 'whatever@gmail.com',
                'cc': ['somebody@gmail.com'],
                'bcc': 'more@gmail.com,andmore@gmail.com',
                'subject': 'Τεστ test',
                'body': 'This is a τεστ on utf8',
                'content': 'html'}
        message = Message(**info)
        self.assertTrue(message.subject == u'Τεστ test')
        self.assertTrue(message.body == u'This is a τεστ on utf8')

    def testTextContent(self):
        info = {'sender': 'test@test.com',
                'recipients': 'whatever@gmail.com',
                'cc': ['somebody@gmail.com'],
                'bcc': 'more@gmail.com,andmore@gmail.com',
                'subject': 'Τεστ test',
                'body': 'This is a τεστ on utf8',
                'content': 'text'}
        message = Message(**info)
        self.assertTrue(message.subject == u'Τεστ test')
        self.assertTrue(message.body == u'This is a τεστ on utf8')

    def testRecipients(self):
        info = {'sender': 'test@test.com',
                'recipients': 'whatever@gmail.com',
                'cc': ['somebody@gmail.com'],
                'bcc': 'more@gmail.com,andmore@gmail.com',
                'subject': 'Τεστ test',
                'body': 'This is a τεστ on utf8',
                'content': 'html'}
        message = Message(**info)
        self.assertTrue(message.recipients == ['whatever@gmail.com',
                                               'somebody@gmail.com',
                                               'more@gmail.com',
                                               'andmore@gmail.com'])

    def testSmtpInstance(self):
        info = {'smtp_address': 'smtp.test.com',
                'username': 'hacker',
                'password': 'whatever',
                'ssl': False,
                'tls': True,
                'port': 587}
        smtp = SmtpServer(**info)
        self.assertTrue(smtp.address == 'smtp.test.com')
        self.assertTrue(smtp.username == 'hacker')
        self.assertTrue(smtp.password == 'whatever')
        self.assertFalse(smtp.ssl)
        self.assertTrue(smtp.tls)
        self.assertTrue(smtp.port == 587)
        self.assertFalse(smtp.connected)

    def tearDown(self):
        """
        Test tear down

        This is where you should tear down what you've setup in setUp before. This method is called after every test.
        """
        pass
