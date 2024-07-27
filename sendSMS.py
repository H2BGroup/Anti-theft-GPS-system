import os

def sendSMS(receiver, content):
    cmd = "gammu-smsd-inject TEXT " + receiver + " -text '"+content+"'"
    os.system(cmd)