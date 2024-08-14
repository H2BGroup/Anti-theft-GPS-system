import os

def sendSMS(receiver, content):
    cmd = "gammu-smsd-inject TEXT " + receiver + " -len " + str(len(content)) + " -text '"+content+"'"
    os.system(cmd)