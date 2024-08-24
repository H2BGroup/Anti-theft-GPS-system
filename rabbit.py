import json
import pika
from location import getLocation
import os
import time

CONFIG_FILE = '/home/ASGDR/Anti-theft-GPS-system/config.json'

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

    if message['request']:
        if message['request'] == 'location':
            latitude, longitude, time = getLocation()
            location = {
                "type": "location",
                "latitude": latitude,
                "longitude": longitude,
                "utc_time": time
            }
            # replyRabbit(json.dumps(location), reply_channel, reply_queue)
            return json.dumps(location)
        if message['request'] == 'status':
            # replyRabbit("My status: status", reply_channel, reply_queue)
            status = {
                "type": "status",
                "battery": "Battery"
            }
            return json.dumps(status)


def checkRabbit():
    os.system("sudo pon rnet")
    time.sleep(1)
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
    time.sleep(1)

    responses = []

    for m in messages:
        res = parseRabbit(m)
        if res != None:
            responses.append(res)

    if len(responses) > 0:
        os.system("sudo pon rnet")
        time.sleep(1)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['rabbit_host'], virtual_host=config['rabbit_user'], credentials=pika.PlainCredentials(config['rabbit_user'], config['rabbit_password'])))

        reply_channel = connection.channel()
        reply_channel.queue_declare(queue=config['owner_number'], durable=True)

        for res in responses:
            replyRabbit(res, reply_channel, config['owner_number'])

        connection.close()
        connection = None
        os.system("sudo poff rnet")
        time.sleep(1)