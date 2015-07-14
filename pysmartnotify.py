#!/usr/bin/env python2

import os, subprocess, collections, smtplib, socket
from email.mime.text import MIMEText

flagged = collections.Counter()

#SMART ID# to check for non zero RAW_VALUEs
check_ids = [1, 5, 7, 10, 11, 196, 197, 198]

#File to store list of flagged drives
flagged_path = '/tmp/flagged_drives.list'

#List of ignored drives
ignored = ['/dev/fd0']

#Number of recurring errors for at least one drive before no more notifications are sent
error_threshold = 3

#List of recipient email addresses
smtp_server = 'smtp.gmail.com'
USERNAME = 'user'
PASSWORD = 'pass'

recipients = ['user@host.tld']
sender = 'someone@somewhere'


def flagged_storage(op):
	"""Handle writing and reading list file of flagged drives."""
	if op == 'w':
		with open(flagged_path, op) as f:
			for k, v in flagged.items():
				f.write("%s:%d\n" % (k, v))
	elif op == 'r' and os.path.isfile(flagged_path):
		with open(flagged_path, op) as f:
			data = f.read().split('\n')[:-1]
			for i in data:
				try:
					k, v = i.split(':')
					flagged[k] = int(v)
				except ValueError:
					print("No data to parse")
	else:
		return False

def error_parser(drive, line):
	"""Checks each line of SMART attributes for problems and flags the drive."""
	problem = 0
	if any(int(line['ID#']) == x for x in check_ids):
		try:
			if int(line['RAW_VALUE']) > 0:
				problem = True
		except ValueError:
			print("RAW_VALUE not INT, ignoring.")

		if line['WHEN_FAILED'] != '-':
			problem = True
		if problem == True:
			flagged[drive] += 1

def mail(content):
	"""Send email with flagged drives counter"""
	msg = MIMEText("Error count per drive: " + str(content), 'plain')
	msg['Subject'] = "SMART Error detected on %s" % socket.getfqdn()
	msg['From'] = sender
	msg['To'] = ", ".join(recipients)

	s = smtplib.SMTP_SSL(smtp_server)
	s.login(USERNAME, PASSWORD)
	s.sendmail(sender, recipients, msg.as_string())
	s.close()
	
def main():
	data = collections.OrderedDict()
	drives = subprocess.check_output(["sudo", "smartctl", "--scan"]).split('\n')[:-1]
	if flagged_storage('r') == False:
		print("File %s does not exist yet, creating." % flagged_path)
	notify = False
	for i in drives:
		i = i.split()
		if i[0] not in ignored:
			smartdata = subprocess.check_output(["sudo", "smartctl", "-A", i[0]])
			smartdata = smartdata.split('\n')

			lines = []
			labels = smartdata[6].split()
			for l in smartdata[7:-2]:
				line = collections.OrderedDict(zip(labels, l.split()))
				lines.append(line)
				error_parser(i[0], line)
			data[i[0]] = lines
		else:
			print("%s is in ignore list, skipping." % i[0])

		if 0 < flagged[i[0]] <= error_threshold:
			notify = True
	if notify == True:
		mail(flagged)

	print(flagged)
	flagged_storage('w')
	

main()

exit(0)
