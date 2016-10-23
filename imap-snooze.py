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
        snoozeboxes = filter(lambda x : str(x).find("pop") != -1, mailboxes)
        self.boxes = list(map(SnoozeBox, snoozeboxes))
        print(self.boxes)

    def loop(self):
        while True:
            print("Checking mailbox again")
            for box in self.boxes:
                self.process(box)
            import time
            time.sleep(60)

    def process(self, box):
        self.markNew(box)
        self.moveBack(box)

    def markNew(self, box):
        self.imap.select(box.name)
        status, data = self.imap.uid('search', None, 'ALL')
        assert(status == "OK")
        mails = data[0].decode("utf-8").split(" ")
        toDelete = []

        if mails == ['']:
            return;

        for mail in mails:
            status, body = self.imap.uid('fetch', mail, '(RFC822)')
            assert(status == "OK")
            body = body[0][1].decode("utf-8")
            if body.find("X-SNOOZE:") == -1:
                import time
                t = int(time.time())
                t += int(box.time) * 3600
                body = "X-SNOOZE: " + str(t) + "\n" + body
                toDelete.append(mail)
                self.imap.append(box.name, None, None, body.encode("utf-8"))
                res = self.imap.uid('STORE', mail, '+FLAGS', '(\Deleted)')

        a = self.imap.expunge()
        return

    def moveBack(self, box):
        self.imap.select(box.name)
        status, data = self.imap.uid('search', None, 'ALL')
        assert(status == "OK")
        mails = data[0].decode("utf-8").split(" ")
        toDelete = []
        if mails == ['']:
            return;

        for mail in mails:
            status, body = self.imap.uid('fetch', mail, '(RFC822)')
            assert(status == "OK")
            body = body[0][1].decode("utf-8")
            import email.feedparser as parser
            p = parser.FeedParser()
            p.feed(body)
            email = p.close()

            if body.find("X-SNOOZE:") != -1:
                import re
                moveTime = int(re.findall(r'\d+', body) [0])
                import time
                currentTime = time.time()
                if moveTime > currentTime:
                    remainingTime = moveTime - currentTime
                    remainingSeconds = remainingTime % 60
                    remainingMinutes = remainingTime % (60 * 60)
                    remainingHours = remainingTime % (60 * 60 * 60)
                    remainingDays = remainingTime

                    remainingSeconds = remainingSeconds
                    remainingMinutes = remainingMinutes / 60
                    remainingHours = remainingHours / (60 * 60)
                    remainingDays = remainingDays / (60 * 60 * 24)

                    print("# Igoring\n\"%s\" from %s" %
                          (email["Subject"], email["From"]))
                    print("Time left: %d d, %d h, %d m, %d s" % (remainingDays, remainingHours, remainingMinutes, remainingSeconds))
                    continue
                body = body[body.find('\n')+1:body.rfind('\n')]
                self.imap.append("INBOX", None, None, body.encode("utf-8"))
                res = self.imap.uid('STORE', mail, '+FLAGS', '(\Deleted)')

        self.imap.expunge()
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
