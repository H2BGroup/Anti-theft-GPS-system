import json
import pika
from location import getLocation
import os
import time
import battery

CONFIG_FILE = '/usr/local/sbin/Anti-theft-GPS-system/config.json'

def replyRabbit(message, reply_channel, reply_queue):
    reply_channel.basic_publish(
        exchange='',
        routing_key=reply_queue,
        body=message)


def parseRabbit(body):
    try:
        message = json.loads(body)
    except json.JSONDecodeError:
        print("Error decoding message")
        return None

    if 'request' in message:
        if message['request'] == 'location':
            latitude, longitude, time = getLocation()
            location = {
                "type": "location",
                "latitude": latitude,
                "longitude": longitude,
                "utc_time": time
            }
            return json.dumps(location)
        if message['request'] == 'status':
            percent, current, utc_time = battery.getBatteryStatus()
            status = {
                "type": "status",
                "percent": percent,
                "charging": True if current > 0 else False,
                "utc_time": utc_time
            }
            return json.dumps(status)


def checkRabbit():
    os.system("sudo pon rnet")
    #wait until network adapter called ppp0 with state UNKNOWN shows up
    while os.system("ip link show | grep ppp0 | grep UNKNOWN > /dev/null") != 0:
        time.sleep(0.5)
    f = open(CONFIG_FILE)
    config = json.load(f)
    f.close()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['rabbit_host'], virtual_host=config['rabbit_user'], credentials=pika.PlainCredentials(config['rabbit_user'], config['rabbit_password'])))
    
    channel = connection.channel()
    channel.queue_declare(queue=config['device_number'], durable=True)

    messages = []

    while True:
        method_frame, header_frame, body = channel.basic_get(queue = config['device_number'])
        if method_frame:
            print(method_frame, header_frame, body)
            messages.append(body)
            # parseRabbit(body, reply_channel, config['owner_number'])
            channel.basic_ack(method_frame.delivery_tag)
        else:
            print('End of messages')
            break
    
    connection.close()
    connection = None
    os.system("sudo poff rnet")
    #wait while device called ppp0 is visible
    while os.system("ip link show | grep ppp0 > /dev/null") == 0:
        time.sleep(0.5)

    responses = []

    for m in messages:
        res = parseRabbit(m)
        if res != None:
            responses.append(res)

    if len(responses) > 0:
        os.system("sudo pon rnet")
        while os.system("ip link show | grep ppp0 | grep UNKNOWN > /dev/null") != 0:
            time.sleep(0.5)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['rabbit_host'], virtual_host=config['rabbit_user'], credentials=pika.PlainCredentials(config['rabbit_user'], config['rabbit_password'])))

        reply_channel = connection.channel()
        reply_channel.queue_declare(queue=config['owner_number'], durable=True)

        for res in responses:
            replyRabbit(res, reply_channel, config['owner_number'])

        connection.close()
        connection = None
        os.system("sudo poff rnet")
        while os.system("ip link show | grep ppp0 > /dev/null") == 0:
            time.sleep(0.5)