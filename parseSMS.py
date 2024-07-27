import os
from sendSMS import sendSMS
from location import getLocation
import json

availableCommands = {
	'location': 'Sends device current location',
	'status': 'Sends device current status (battery, connection, etc.)',
}

def parseSMS(sender, content):
	if content == "location":
		location = getLocation()
		sendSMS(sender, f"My location: {location}")
		return
	if content == "status":
		sendSMS(sender, "My status: status")
		return
	sendSMS(sender, "Unknown command, my commands are: \n"+json.dumps(availableCommands, indent='\n')[2:-1])
