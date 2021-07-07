#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: emaillib.py
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
Main code for emaillib.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
import os
import re
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, parseaddr

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''16-09-2017'''
__copyright__ = '''Copyright 2017, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''emaillib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class SmtpServer:  # pylint: disable=too-many-instance-attributes
    """A simple wrapper around build in smtplib capabilities."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 smtp_address,
                 username=None,
                 password=None,
                 tls=True,
                 ssl=False,
                 port=None):
        self._smtp = None
        self._address = smtp_address
        self._tls = tls
        self._ssl = ssl
        self._port = port
        self._username = username
        self._password = password
        self._connected = False
        self._logger = logging.getLogger(__name__)

    @property
    def tls(self):
        """The setting of tls upon instantiation."""
        return self._tls

    @property
    def ssl(self):
        """The setting of ssl upon instantiation."""
        return self._ssl

    @property
    def username(self):
        """The username upon instantiation."""
        return self._username

    @property
    def password(self):
        """The password upon instantiation."""
        return self._password

    @property
    def address(self):
        """The smtp server address upon instantiation."""
        return self._address

    @property
    def port(self):
        """The smtp server port upon instantiation."""
        return self._port

    @property
    def connected(self):
        """The status of connection to the smtp server."""
        return self._connected

    def connect(self):
        """Initializes a connection to the smtp server.

        :return: True on success, False otherwise
        """
        connection_method = 'SMTP_SSL' if self.ssl else 'SMTP'
        self._logger.debug('Trying to connect via {}'.format(connection_method))
        smtp = getattr(smtplib, connection_method)
        if self.port:
            self._smtp = smtp(self.address, self.port)
        else:
            self._smtp = smtp(self.address)
        self._smtp.ehlo()
        if self.tls:
            self._smtp.starttls()
            self._smtp.ehlo()
        self._logger.info('Got smtp connection')
        if self.username and self.password:
            self._logger.info('Logging in')
            self._smtp.login(self.username, self.password)
        self._connected = True

    def send(self,  # pylint: disable=too-many-arguments, invalid-name
             sender,
             recipients,
             cc=None,
             bcc=None,
             subject='',
             body='',
             attachments=None,
             content='text'):
        """Sends the email.

        :param sender: The server of the message
        :param recipients: The recipients (To:) of the message
        :param cc: The CC recipients of the message
        :param bcc: The BCC recipients of the message
        :param subject: The subject of the message
        :param body: The body of the message
        :param attachments: The attachments of the message
        :param content: The type of content the message [text/html]

        :return: True on success, False otherwise
        """
        if not self.connected:
            self._logger.error(('Server not connected, cannot send message, '
                                'please connect() first and disconnect() when '
                                'the connection is not needed any more'))
            return False
        try:
            message = Message(sender,
                              recipients,
                              cc,
                              bcc,
                              subject,
                              body,
                              attachments,
                              content)
            self._smtp.sendmail(message.sender,
                                message.recipients,
                                message.as_string)
            result = True
            self._connected = False
            self._logger.debug('Done')
        except Exception:  # noqa
            self._logger.exception('Something went wrong!')
            result = False
        return result

    def disconnect(self):
        """Disconnects from the remote smtp server.

        :return: True on success, False otherwise
        """
        if not self.connected:
            return True
        try:
            self._smtp.close()
            self._connected = False
            result = True
        except Exception:  # noqa
            self._logger.exception('Something went wrong!')
            result = False
        return result


class EasySender:  # pylint: disable=too-few-public-methods, too-many-arguments, invalid-name
    """A simple wrapper around the SmtpServer object."""

    def __init__(self,
                 smtp_address,
                 username=None,
                 password=None,
                 tls=False,
                 ssl=True,
                 port=None):
        self._server = SmtpServer(smtp_address,
                                  username,
                                  password,
                                  tls,
                                  ssl,
                                  port)

    def send(self,
             sender,
             recipients,
             cc=None,
             bcc=None,
             subject='',
             body='',
             attachments=None,
             content='text'):
        """Sends the email by connecting and disconnecting after the send.

        :param sender: The sender of the message
        :param recipients: The recipients (To:) of the message
        :param cc: The CC recipients of the message
        :param bcc: The BCC recipients of the message
        :param subject: The subject of the message
        :param body: The body of the message
        :param attachments: The attachments of the message
        :param content: The type of content the message [text/html]

        :return: True on success, False otherwise
        """
        self._server.connect()
        self._server.send(sender,
                          recipients,
                          cc,
                          bcc,
                          subject,
                          body,
                          attachments,
                          content)
        self._server.disconnect()
        return True


class Message:  # pylint: disable=too-many-instance-attributes
    """A model of an email message."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 sender,
                 recipients,
                 cc=None,
                 bcc=None,
                 subject='',
                 body='',
                 attachments=None,
                 content='text'):
        self._sender = None
        self._recipients = None
        self._to = []
        self._cc = []
        self._bcc = []
        self._subject = None
        self._body = None
        self._attachments = None
        self._parts = None
        self._content = None
        self._message = None
        self.sender = sender
        self.to = recipients  # pylint: disable=invalid-name
        self.cc = cc  # pylint: disable=invalid-name
        self.bcc = bcc
        self.subject = subject
        self.body = body
        self.attachments = attachments
        self.content = content
        self._setup_message()

    def _setup_message(self):
        """Constructs the actual underlying message with provided values.."""
        if self.content == 'html':
            self._message = MIMEMultipart('alternative')
            part = MIMEText(self.body, 'html', 'UTF-8')
        else:
            self._message = MIMEMultipart()
            part = MIMEText(self.body, 'plain', 'UTF-8')
        self._message.preamble = 'Multipart massage.\n'
        self._message.attach(part)
        self._message['From'] = self.sender
        self._message['To'] = COMMASPACE.join(self.to)
        if self.cc:
            self._message['Cc'] = COMMASPACE.join(self.cc)
        self._message['Date'] = formatdate(localtime=True)
        self._message['Subject'] = self.subject
        for part in self._parts:
            self._message.attach(part)

    @staticmethod
    def _validate_simple(email):
        """Does a simple validation of an email by matching it to a regex.

        :param email: The email to check
        :return: The valid Email address

        :raises: ValueError if value is not a valid email
        """
        _, address = parseaddr(email)
        if not re.match(r'[^@]+@[^@]+\.[^@]+', address):
            raise ValueError('Invalid email :{email}'.format(email=email))
        return address

    @staticmethod
    def _comma_delimited_to_list(value):
        if not isinstance(value, (list, tuple)):
            return [entry.strip() for entry in value.split(',')]
        return value

    @property
    def sender(self):
        """The email address of the sender."""
        return self._sender

    @sender.setter
    def sender(self, value):
        if not value:
            raise ValueError('Sender cannot be empty.')
        self._sender = self._validate_simple(value)

    @property
    def recipients(self):
        """A list of all recipients of the message."""
        return self.to + self.cc + self.bcc

    def _get_recipients(self, value):
        recipients = self._comma_delimited_to_list(value) if value else []
        return [self._validate_simple(recipient) for recipient in recipients]

    @property
    def to(self):  # pylint: disable=invalid-name
        """The main (to) recipients of the message."""
        return self._to

    @to.setter
    def to(self, value):  # pylint: disable=invalid-name
        if not value:
            raise ValueError('Recipients cannot be empty.')
        self._to = self._get_recipients(value)

    @property
    def cc(self):  # pylint: disable=invalid-name
        """The cc recipients of the message."""
        return self._cc

    @cc.setter
    def cc(self, value):  # pylint: disable=invalid-name
        self._cc = self._get_recipients(value)

    @property
    def bcc(self):
        """The bcc recipients of the message."""
        return self._bcc

    @bcc.setter
    def bcc(self, value):
        self._bcc = self._get_recipients(value)

    @property
    def subject(self):
        """The subject of the message."""
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def body(self):
        """The body of the message."""
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def content(self):
        """The type of content of the message."""
        return self._content

    @content.setter
    def content(self, value):
        if value.lower() not in ['text', 'html']:
            raise ValueError(('Invalid content type :{content}.'
                              'Allowed ["text", "html"]').format(content=value))
        self._content = value.lower()

    @property
    def attachments(self):
        """A list of attachment names of the message."""
        return self._attachments

    @attachments.setter
    def attachments(self, entries):
        values = []
        self._parts = []
        attachments = self._comma_delimited_to_list(entries) if entries else []
        for attachment in attachments:
            part = MIMEApplication(open(os.path.expanduser(attachment),
                                        "rb").read())
            part.add_header('Content-Disposition',
                            'attachment',
                            filename=os.path.basename(attachment))
            self._parts.append(part)
            values.append(attachment)
        self._attachments = values

    @property
    def as_string(self):
        """The string representation of the message."""
        return self._message.as_string()

    def __str__(self):
        """The string representation of the message."""
        return self.as_string
