#!/usr/bin/env python

import os, subprocess, collections

flagged = collections.Counter()

#SMART ID# to check for non zero RAW_VALUEs
check_ids = [1, 5, 7, 10, 11, 194, 196, 197, 198]

#Handle writing and reading list of flagged drives
def flagged_storage(op):
	path = "flagged_drives.list"
	if op == 'w':
		f = open(path, op)
		for k, v in flagged.items():
			f.write("%s:%d\n" % (k, v))
		return(0)
	elif op == 'r' and os.path.isfile(path):
		f = open(path, op)
		data = f.read().split('\n')[:-1]
		for i in data:
			try:
				k, v = i.split(':')
				flagged[k] = int(v)
			except ValueError:
				print("No data to parse\n")
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
			print("RAW_VALUE not INT, ignoring.\n")
	
		if line['WHEN_FAILED'] != '-':
			problem = 1
		if problem == 1:
			flagged[drive] += 1


def main():
	data = collections.OrderedDict()
	drives = subprocess.check_output(["lsblk", "-nlS", "-o", "NAME"]).split('\n')[:-1]
	flagged_storage('r')
	for i in drives:
		smartdata = subprocess.check_output(["sudo", "smartctl", "-A", "/dev/" + i])
		smartdata = smartdata.split('\n')

		lines = []
		labels = smartdata[6].split()
		for l in smartdata[7:-2]:
			line = dict(zip(labels, l.split()))
			lines.append(line)
			error_parser(i, line)
	
	print(flagged)
	flagged_storage('w')
	data["/dev/" + i] = lines



main()

exit(0)
