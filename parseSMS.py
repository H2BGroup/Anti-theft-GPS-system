from sendSMS import sendSMS
from location import getLocation
import json

CONFIG_FILE = '/home/ASGDR/Anti-theft-GPS-system/config.json'

availableCommands = {
	'location': 'Sends device current location',
	'status': 'Sends device current status (battery, connection, etc.)',
}

def parseSMS(state_machine, sender, content):
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
		sendSMS(state_machine, sender, f"Hello new user, the device has been successfully linked. You can now use my commands: \n"+json.dumps(availableCommands, indent='\n')[2:-1])
		return

	if sender != owner_number:
		return

	if content == "location":
		latitude, longitude, time = getLocation()
		if latitude != None:
			sendSMS(state_machine, sender, f"My location: {latitude},{longitude}\nhttps://www.google.com/maps/search/?api=1&query={latitude},{longitude}\n{time}")
		else:
			sendSMS(state_machine, sender, "Cant get location right now, try again later")
		return
	if content == "status":
		sendSMS(state_machine, sender, "My status: status")
		return
	sendSMS(state_machine, sender, "Unknown command, my commands are: \n"+json.dumps(availableCommands, indent='\n')[2:-1])
