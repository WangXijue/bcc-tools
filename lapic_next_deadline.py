#!/usr/bin/python
#
# Written as a basic example of a function latency distribution histogram.
#
# USAGE: lapic_next_deadline.py [interval [count]]
#
# The default interval is 10 seconds. A Ctrl-C will print the partially
# gathered histogram then exit.
#
# Copyright (c) 2015 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 15-Aug-2015	Brendan Gregg	Created this.

from __future__ import print_function
from bcc import BPF
from ctypes import c_ushort, c_int, c_ulonglong
from time import sleep
from sys import argv

def usage():
	print("USAGE: %s [interval [count]]" % argv[0])
	exit()

# arguments
interval = 10
count = -1
if len(argv) > 1:
	try:
		interval = int(argv[1])
		if interval == 0:
			raise
		if len(argv) > 2:
			count = int(argv[2])
	except:	# also catches -h, --help
		usage()

# load BPF program
b = BPF(src_file = "lapic_next_deadline.c")
b.attach_kprobe(event="lapic_next_deadline", fn_name="do_entry")
b.attach_kretprobe(event="lapic_next_deadline", fn_name="do_return")

# header
print("Tracing... Hit Ctrl-C to end.")

# output
loop = 0
do_exit = 0
while (1):
	if count > 0:
		loop += 1
		if loop > count:
			exit()
	try:
		sleep(interval)
	except KeyboardInterrupt:
		pass; do_exit = 1

	print()
	b["dist"].print_log2_hist("nsecs")
	b["dist"].clear()
	if do_exit:
		exit()

