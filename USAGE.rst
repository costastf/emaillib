=====
Usage
=====

To use emaillib in a project:

.. code-block:: python

    # to easily just send a message
    from emaillib import EasySender

    smtp = {'address': 'smtp.domain.com',
            'username': 'usersName',
            'password': 'usersPassword',
            'port': 587}
    info = {'sender': 'test@test.com',
            'recipients': 'whatever@gmail.com',
            'cc': ['somebody@gmail.com'],
            'bcc': 'more@gmail.com,andmore@gmail.com',
            'subject': 'Τεστ test',
            'body': 'This is a τεστ on utf8'}

    server = EasySender(**smtp)
    server.send(**info)


    # to use a more constant server connection where you can connect and
    # disconnect as required

    from emaillib import SmtpServer

    smtp = {'address': 'smtp.domain.com',
            'username': 'usersName',
            'password': 'usersPassword',
            'port': 587}
    info = {'sender': 'test@test.com',
            'recipients': 'whatever@gmail.com',
            'cc': ['somebody@gmail.com'],
            'bcc': 'more@gmail.com,andmore@gmail.com',
            'subject': 'Τεστ test',
            'body': 'This is a τεστ on utf8'}

    server = SmtpServer(**smtp)
    server.connect()
    server.send(**info)
    server.disconnect()


    # a message can manually be constructed
    # values for recipients, cc and bcc can be either lists or tuples, or comma
    # delimited text. Internally those will be transformed to lists.
    from emaillib import Message

    info = {'sender': 'test@test.com',
            'recipients': 'whatever@gmail.com',
            'cc': ['somebody@gmail.com'],
            'bcc': 'more@gmail.com,andmore@gmail.com',
            'subject': 'Τεστ test',
            'body': 'This is a τεστ on utf8'}

    message = Message(**info)

    # show all the recipients
    print(message.recipients)
    # >>> ['whatever@gmail.com', 'somebody@gmail.com', 'more@gmail.com', 'andmore@gmail.com']

    # show only "to" recipients
    print(message.to)
    # >>> ['whatever@gmail.com']

    # show only "cc" recipients
    print(message.cc)
    # >>> ['somebody@gmail.com']

    # show only "bcc" recipients
    print(message.bcc)
    # >>> ['more@gmail.com', 'andmore@gmail.com']

    # and its string representation can be accessed as
    print(message.as_string)
