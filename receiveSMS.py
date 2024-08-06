#!/usr/bin/env python

import os
import sys
import parseSMS
import subprocess
import time

def get_pid(process_name):
    """Get the PID of the process by name."""
    try:
        pid = subprocess.check_output(['pidof', process_name]).strip().decode('utf-8')
        return pid
    except subprocess.CalledProcessError:
        return None
    
def send_signal(pid, signal):
    """Send a signal to the process with the given PID."""
    subprocess.run(['kill', f'-{signal}', pid])

numparts = int(os.environ["DECODED_PARTS"])

text = ""
# Are there any decoded parts?
if numparts == 0:
    text = os.environ["SMS_1_TEXT"]
# Get all text parts
else:
    for i in range(1, numparts + 1):
        varname = "DECODED_%d_TEXT" % i
        if varname in os.environ:
            text = text + os.environ[varname]

# Do something with the text
print("Number {} have sent text: {}".format(os.environ["SMS_1_NUMBER"], text))
pid = os.fork()
if pid:
    #parent
    pass
else:
    #child
    smsd_pid = get_pid('gammu-smsd')
    send_signal(smsd_pid, 'SIGUSR1')
    time.sleep(1)
    parseSMS.parseSMS(os.environ["SMS_1_NUMBER"], text)
    send_signal(smsd_pid, 'SIGUSR2')
    sys.exit()
