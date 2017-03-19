# Script to add "Snooze" on fastmail servers

## Prepare your mailbox

Setup mailbox folders named:

	x-snooze-1
	x-snooze-2
	x-snooze-3
	...
	x-snooze-7

The number in the mailbox specifies for how many days mails should be snoozed.

## Mark an email to be snoozed

By typing "m" and then "x", you can quickly move an email into the snooze
folder.

## Run imap-snooze.py to ensure emails are moved back to INBOX

Clone this repository and run:

imap-snooze.py --user fastmailusername --password application-password

** Warning: only use on machines which you own. Other users on shared machines
   can often access the command line arguments and can consequently steal your
   password **

** Warning: this is beta software. I use it myself, but this is an early
   prototype, which may have serious bugs.**
