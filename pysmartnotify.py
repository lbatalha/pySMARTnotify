#!/usr/bin/env python

import os, subprocess, collections, smtplib, socket, json
from email.mime.text import MIMEText

flagged = collections.Counter()

#SMART ID# to check for non zero RAW_VALUEs
check_ids = [1, 5, 7, 10, 11, 196, 197, 198]

#File to store list of flagged drives
flagged_path = "flagged_drives.list"

#List of ignored drives (floppy et al)
ignored = ['fd0']

#List of recipient email addresses
smtp_server = 'smtp.gmail.com'
USERNAME = ''
PASSWORD = ''

recipients = ['']
sender = ''


#Handle writing and reading list of flagged drives
def flagged_storage(op):
	if op == 'w':
		f = open(flagged_path, op)
		for k, v in flagged.items():
			f.write("%s:%d\n" % (k, v))
		f.close()
		return(0)
	elif op == 'r' and os.path.isfile(flagged_path):
		f = open(flagged_path, op)
		data = f.read().split('\n')[:-1]
		for i in data:
			try:
				k, v = i.split(':')
				flagged[k] = int(v)
			except ValueError:
				print("No data to parse")
		f.close()
		return(0)
	else:
		return(1)

#Checks each line of SMART attributes for problems and flags them
def error_parser(drive, line):
	problem = 0
	if any(int(line['ID#']) == x for x in check_ids):
		try:
			if int(line['RAW_VALUE']) > 0:
				problem = 1
		except ValueError:
			print("RAW_VALUE not INT, ignoring.")
	
		if line['WHEN_FAILED'] != '-':
			problem = 1
		if problem == 1:
			flagged[drive] += 1

def notify(content):
	body = json.dumps(content, indent=4)
	msg = MIMEText(body, 'plain')
	msg['Subject'] = "SMART Error detected on %s" % socket.getfqdn()
	msg['From'] = sender
	msg['To'] = ", ".join(recipients)

	s = smtplib.SMTP_SSL(smtp_server)
	s.login(USERNAME, PASSWORD)
	s.sendmail(sender, recipients, msg.as_string())
	s.close()
	return(0)
	
def main():
	data = collections.OrderedDict()
	drives = subprocess.check_output(["lsblk", "-nlS", "-o", "NAME"]).split('\n')[:-1]
	if flagged_storage('r') != 0:
		print("File %s does not exist yet.\n" % flagged_path)
	for i in drives:
		if ignored.count(i) == 0:
			smartdata = subprocess.check_output(["sudo", "smartctl", "-A", "/dev/" + i])
			smartdata = smartdata.split('\n')

			lines = []
			labels = smartdata[6].split()
			for l in smartdata[7:-2]:
				line = collections.OrderedDict(zip(labels, l.split()))
				lines.append(line)
				error_parser(i, line)
			data["/dev/" + i] = lines
		else:
			print("%s is in ignore list, skipping." % i)
	print(flagged)
	if flagged_storage('w') != 0:
		print("Failed writing %s" % flagged_path)


	if notify(data) != 0:
		print("Failed to send notification type: %s" % notify_method)
		
main()

exit(0)
