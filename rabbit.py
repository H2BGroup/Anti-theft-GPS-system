import json
import pika
from location import getLocation

CONFIG_FILE = '/home/ASGDR/Anti-theft-GPS-system/config.json'

def replyRabbit(message, reply_channel, reply_queue):
    reply_channel.basic_publish(
        exchange='',
        routing_key=reply_queue,
        body=message)


def parseRabbit(body, reply_channel, reply_queue):
    try:
        message = json.loads(body)
    except json.JSONDecodeError:
        print("Error decoding message")
        return

    if message['request']:
        if message['request'] == 'location':
            location = getLocation()
            replyRabbit(location, reply_channel, reply_queue)
            return
        if message['request'] == 'status':
            replyRabbit("My status: status", reply_channel, reply_queue)
            return


def checkRabbit():
    f = open(CONFIG_FILE)
    config = json.load(f)
    f.close()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['rabbit_host'], virtual_host=config['rabbit_user'], credentials=pika.PlainCredentials(config['rabbit_user'], config['rabbit_password'])))
    
    channel = connection.channel()
    channel.queue_declare(queue=config['device_number'], durable=True)

    reply_channel = connection.channel()
    reply_channel.queue_declare(queue=config['owner_number'], durable=True)

    while True:
        method_frame, header_frame, body = channel.basic_get(queue = config['device_number'])
        if method_frame:
            print(method_frame, header_frame, body)
            parseRabbit(body, reply_channel, config['owner_number'])
            channel.basic_ack(method_frame.delivery_tag)
        else:
            print('End of messages')
            break

    connection.close()