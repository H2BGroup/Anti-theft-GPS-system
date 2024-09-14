import json
import pika
from location import getLocation
import os
import time
import battery

CONFIG_FILE = '/usr/local/sbin/Anti-theft-GPS-system/config.json'
TEMP_MESSAGE_FILE = '/usr/local/sbin/Anti-theft-GPS-system/rabbit_temp.json'

PPP_TIMEOUT = 10.0 #seconds

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
            return location
        if message['request'] == 'status':
            percent, current, utc_time = battery.getBatteryStatus()
            status = {
                "type": "status",
                "percent": percent,
                "charging": True if current > 0 else False,
                "utc_time": utc_time
            }
            return status
        return None


def checkRabbit():
    os.system("sudo pon rnet")
    #wait until network adapter called ppp0 with state UNKNOWN shows up
    wait_ppp = 0
    while os.system("ip link show | grep ppp0 | grep UNKNOWN > /dev/null") != 0:
        print("waiting for ppp0")
        time.sleep(0.5)
        wait_ppp+=0.5
        if wait_ppp >= PPP_TIMEOUT:
            raise SystemExit("Error setting up pppd")
        
    print("internet connection successfull")
    f = open(CONFIG_FILE)
    config = json.load(f)
    f.close()

    connection = pika.BlockingConnection(pika.ConnectionParameters(
                                        host=config['rabbit_host'], 
                                        virtual_host=config['rabbit_user'], 
                                        credentials=pika.PlainCredentials(config['rabbit_user'], config['rabbit_password']), 
                                        socket_timeout=20.0,
                                        stack_timeout=30.0,
                                        retry_delay=5.0,
                                        connection_attempts=3))
    
    channel = connection.channel()
    channel.queue_declare(queue=config['device_number'], durable=True)
    print("connected to rabbit")

    # send responses from previous cycle
    previous_responses = []
    
    try:
        temp_file = open(TEMP_MESSAGE_FILE)
        previous_responses = json.load(temp_file)
        temp_file.close()
    except:
        previous_responses = []
    
    if len(previous_responses) > 0:
        print("Sending responses from previous cycle")
        reply_channel = connection.channel()
        reply_channel.queue_declare(queue=config['owner_number'], durable=True)

        for res in previous_responses:
            res_str = json.dumps(res)
            replyRabbit(res_str, reply_channel, config['owner_number'])
        
        # clear outgoing messages queue
        temp_file = open(TEMP_MESSAGE_FILE)
        json.dump([], temp_file)
        temp_file.close()

    # receive new messages
    print("Downloading new messages")
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
        print("waiting for ppp0 to turn off")
        time.sleep(0.5)
    time.sleep(1)
    print("Preparing responses")
    responses = []

    for m in messages:
        res = parseRabbit(m)
        if res != None:
            responses.append(res)
    
    if len(responses) > 0:
        #save responses for next cycle
        temp_file = open(TEMP_MESSAGE_FILE, 'w')
        json.dump(responses, temp_file)
        temp_file.close()