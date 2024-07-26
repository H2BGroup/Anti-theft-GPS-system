import os

def parseSMS(sender, content):
	if content == "location":
		cmd = "gammu-smsd-inject TEXT " + sender + " -text 'My location: "+content+"'"
		os.system(cmd)
		
