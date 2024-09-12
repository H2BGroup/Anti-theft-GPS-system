from location import getLocation
import battery
import json

CONFIG_FILE = '/usr/local/sbin/Anti-theft-GPS-system/config.json'

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
		return (sender, f"Hello new user, the device has been successfully linked. You can now use my commands: \n"+json.dumps(availableCommands, indent='\n')[2:-1])

	if sender != owner_number:
		return None

	if content == "location":
		latitude, longitude, time = getLocation()
		if latitude != None:
			return (sender, f"My location: {latitude},{longitude}\nhttps://www.google.com/maps/search/?api=1&query={latitude},{longitude}\n{time}")
		else:
			return (sender, "Cant get location right now, try again later")
	if content == "status":
		percent, current, utc_time = battery.getBatteryStatus()
		if percent != None:
			return (sender, f"Status:\nBattery: {percent:3.1f}% {'Charging' if current > 0 else 'Unplugged'}")
		else:
			return (sender, "Status: Unknown battery status")
	
	return (sender, "Unknown command, my commands are: \n"+json.dumps(availableCommands, indent='\n')[2:-1])
