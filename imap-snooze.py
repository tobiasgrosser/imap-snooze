#!/usr/bin/env python3

from imaplib import IMAP4_SSL

class SnoozeBox:
    """
    A snooze box is an imap folder that contains the string "snooze" and a
    number that defines the number of days a message in this folder should be
    snoozed.
    """
    def __init__(self, string):
        self.bstring = string
        self.name = string.decode("utf-8")[7:]

        import re
        self.time = re.findall(r'\d+', self.name) [0]

    def __str__(self):
        return "SnoozeBox(\"" + self.name + "\", "+ self.time + ")"

    def __repr__(self):
        return str(self)

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

    def findSnoozeBoxes(self):
        status , mailboxes = self.imap.lsub()
        assert(status == "OK")
        snoozeboxes = filter(lambda x : str(x).find("snooze") != -1, mailboxes)
        self.boxes = list(map(SnoozeBox, snoozeboxes))
        print(self.boxes)

    def loop(self):
        while True:
            for box in self.boxes:
                self.process(box)
            import time
            time.sleep(5)

    def process(self, box):
        self.markNew(box)

    def markNew(self, box):
        self.imap.select(box.name)
        status, data = self.imap.uid('search', None, 'NOT HEADER SNOOZE ".*"')
        assert(status == "OK")
        mails = data[0].decode("utf-8").split(" ")
        toDelete = []

        for mail in mails:
            status, body = self.imap.uid('fetch', mail, '(RFC822)')
            assert(status == "OK")
            body = body[0][1].decode("utf-8")
            if body.find("X-SNOOZE:") == -1:
                import time
                t = int(time.time())
                t += int(box.time) * 60
                body = "X-SNOOZE: " + str(t) + "\n" + body
                toDelete.append(mail)
                self.imap.append(box.name, None, None, body.encode("utf-8"))
                res = self.imap.uid('STORE', mail, '+FLAGS', '(\Deleted)')

        a = self.imap.expunge()
        return

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
snoozed.findSnoozeBoxes()
snoozed.loop()
