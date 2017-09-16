#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
# File: emaillib.py
"""Main module file"""

import logging
import os
import smtplib
import re
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate, parseaddr

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = 'plaintext'
__date__ = '''16-09-2017'''

# This is the main prefix used for logging
LOGGER_BASENAME = '''emaillib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class SmtpServer(object):
    """A simple wrapper around build in smtplib capabilities"""

    def __init__(self,
                 address,
                 username=None,
                 password=None,
                 tls=True,
                 ssl=False,
                 port=None):
        self._smtp = None
        self._address = address
        self._tls = tls
        self._ssl = ssl
        self._port = port
        self._username = username
        self._password = password
        self._connected = False
        self._logger = logging.getLogger(__name__)

    @property
    def tls(self):
        """The setting of tls upon instantiation"""
        return self._tls

    @property
    def ssl(self):
        """The setting of ssl upon instantiation"""
        return self._ssl

    @property
    def username(self):
        """The username upon instantiation"""
        return self._username

    @property
    def password(self):
        """The password upon instantiation"""
        return self._password

    @property
    def address(self):
        """The smtp server address upon instantiation"""
        return self._address

    @property
    def port(self):
        """The smtp server port upon instantiation"""
        return self._port

    @property
    def connected(self):
        """The status of connection to the smtp server"""
        return self._connected

    def connect(self):
        """Initializes a connection to the smtp server

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

    def send(self,
             sender,
             recipients,
             cc=None,
             bcc=None,
             subject='',
             body='',
             attachments=None,
             content='text'):
        """Sends the email

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
        """Disconnects from the remote smtp server

        :return: True on success, False otherwise
        """
        if self.connected:
            try:
                self._smtp.close()
                self._connected = False
                result = True
            except Exception:  # noqa
                self._logger.exception('Something went wrong!')
                result = False
            return result


class EasySender(object):
    """A simple wrapper around the SmtpServer object"""

    def __init__(self,
                 address,
                 username=None,
                 password=None,
                 tls=False,
                 ssl=True):
        self._server = SmtpServer(address, username, password, tls, ssl)

    def send(self,
             sender,
             recipients,
             cc=None,
             bcc=None,
             subject='',
             body='',
             attachments=None,
             content='text'):
        """Sends the email by connecting and disconnecting after the send

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


class Message(object):
    """A model of an email message"""

    def __init__(self,
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
        self.to = recipients
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.body = body
        self.attachments = attachments
        self.content = content
        self._setup_message()

    def _setup_message(self):
        """Constructs the actual underlying message with provided values"""
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
        """Does a simple validation of an email by matching it to a regexps

        :param email: The email to check
        :return: The valid Email address

        :raises: ValueError if value is not a valid email
        """
        name, address = parseaddr(email)
        if not re.match('[^@]+@[^@]+\.[^@]+', address):
            raise ValueError('Invalid email :{email}'.format(email=email))
        return address

    @staticmethod
    def _comma_delimited_to_list(value):
        if not isinstance(value, (list, tuple)):
            return [entry.strip() for entry in value.split(',')]
        return value

    @property
    def sender(self):
        """The email address of the sender"""
        return self._sender

    @sender.setter
    def sender(self, value):
        if not value:
            raise ValueError('Sender cannot be empty.')
        self._sender = self._validate_simple(value)

    @property
    def recipients(self):
        """A list of all recipients of the message"""
        return self.to + self.cc + self.bcc

    def _get_recipients(self, value):
        recipients = self._comma_delimited_to_list(value) if value else []
        return [self._validate_simple(recipient) for recipient in recipients]

    @property
    def to(self):
        """The main (to) recipients of the message"""
        return self._to

    @to.setter
    def to(self, value):
        if not value:
            raise ValueError('Recipients cannot be empty.')
        self._to = self._get_recipients(value)

    @property
    def cc(self):
        """The cc recipients of the message"""
        return self._cc

    @cc.setter
    def cc(self, value):
        self._cc = self._get_recipients(value)

    @property
    def bcc(self):
        """The bcc recipients of the message"""
        return self._bcc

    @bcc.setter
    def bcc(self, value):
        self._bcc = self._get_recipients(value)

    @property
    def subject(self):
        """The subject of the message"""
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value.decode('utf-8')

    @property
    def body(self):
        """The body of the message"""
        return self._body

    @body.setter
    def body(self, value):
        self._body = value.decode('utf-8')

    @property
    def content(self):
        """The type of content of the message"""
        return self._content

    @content.setter
    def content(self, value):
        if value.lower() not in ['text', 'html']:
            raise ValueError(('Invalid content type :{content}.'
                              'Allowed ["text", "html"]').format(content=value))
        self._content = value.lower()

    @property
    def attachments(self):
        """A list of attachment names of the message"""
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
        """The string representation of the message"""
        return self._message.as_string()

    def __str__(self):
        """The string representation of the message"""
        return self.as_string
