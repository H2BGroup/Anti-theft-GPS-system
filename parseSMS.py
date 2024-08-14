import os
from sendSMS import sendSMS
from location import getLocation
import json

CONFIG_FILE = '/home/ASGDR/Anti-theft-GPS-system/config.json'

availableCommands = {
	'location': 'Sends device current location',
	'status': 'Sends device current status (battery, connection, etc.)',
}

def parseSMS(sender, content):
	f = open(CONFIG_FILE)
	data = json.load(f)
	f.close()

	owner_number = data['owner_number']
	device_secret = data['device_secret']

	if content == device_secret:
		print("Setting new owner")
		data['owner_number'] = sender
		f = open(CONFIG_FILE, 'w')
		json.dump(data, f)
		f.close()
		sendSMS(sender, f"Hello new user, the device has been successfully linked. You can now use my commands: \n"+json.dumps(availableCommands, indent='\n')[2:-1])
		return

	if sender != owner_number:
		return

	if content == "location":
		location = getLocation()
		sendSMS(sender, f"My location: {location}")
		return
	if content == "status":
		sendSMS(sender, "My status: status")
		return
	sendSMS(sender, "Unknown command, my commands are: \n"+json.dumps(availableCommands, indent='\n')[2:-1])
