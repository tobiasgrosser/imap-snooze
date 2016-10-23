#!/usr/bin/env python3

from imaplib import IMAP4_SSL

class IMAPSnoozeDaemon:
    """
    A snooze daemon which watches a set of IMAP folders for snooze emails to
    appear. If a snooze email appears, it is marked with the time it was moved
    to the snooze folder and is moved back to the main folder when the defined
    snooze delay was reached.
    """
    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password 

    def connect(self):
        self.imap = IMAP4_SSL(self.server)
        self.imap.login(self.user, self.password)

import argparse

parser = argparse.ArgumentParser(description='IMAP snooze daemon.')
parser.add_argument('--server', dest='server', required=True,
                    help='The URL of the imap server to connect to')
parser.add_argument('--user', dest='user', required=True,
                    help='The username to use')
parser.add_argument('--password', dest='password', required=True,
                    help='the password to use')
args = parser.parse_args()


snoozed = IMAPSnoozeDaemon(args.server, args.user, args.password)
snoozed.connect()
