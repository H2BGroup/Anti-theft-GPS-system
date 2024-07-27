import os
from sendSMS import sendSMS
from location import getLocation

def parseSMS(sender, content):
	if content == "location":
		location = getLocation()
		sendSMS(sender, f"My location: {location}")
		return
