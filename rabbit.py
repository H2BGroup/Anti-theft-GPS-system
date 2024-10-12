import json
import pika
from location import getLocation
import os
import time
import battery
import queue

CONFIG_FILE = '/usr/local/sbin/Anti-theft-GPS-system/config.json'
TEMP_MESSAGE_FILE = '/usr/local/sbin/Anti-theft-GPS-system/rabbit_temp.json'

PPP_TIMEOUT = 20.0 #seconds

def setupPPP():
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
    return True

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
            f = open(CONFIG_FILE)
            config = json.load(f)
            f.close()
            percent, current, utc_time = battery.getBatteryStatus()
            status = {
                "type": "status",
                "percent": percent,
                "charging": True if current > 0 else False,
                "device_armed": config['armed'],
                "utc_time": utc_time
            }
            return status
        return None
    
    elif 'armed' in message:
        armed = message['armed']
        print(f'ARMED: {armed}, type: {type(armed)}')

        f = open(CONFIG_FILE)
        config = json.load(f)
        f.close()

        config['armed'] = armed

        f = open(CONFIG_FILE, 'w')
        json.dump(config, f)
        f.close()

        response = {
            "device_armed": armed
        }
        return response
    return None


def checkRabbit(acc_queue: queue.Queue):
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
        temp_file = open(TEMP_MESSAGE_FILE, 'w')
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

    # check if device armed
    if 'armed' in config:
        if config['armed'] == True:
            print("device armed, will send update")
            messages.append('{"request": "location"}'.encode())
            messages.append('{"request": "status"}'.encode())


    print("Preparing responses")
    # respond to each type of message once (no need to send the same location x times) ((except armed/disarmed))
    unique_messages = []
    for m in messages:
        mess = m.decode("utf-8")
        if ('armed' in mess) or (mess not in unique_messages):
            unique_messages.append(mess)
    print(f"Received messages: \n{unique_messages}")

    responses = []

    for m in unique_messages:
        res = parseRabbit(m)
        if res != None:
            responses.append(res)
    
    #check if accelerometer detected movement
    try:
        m = acc_queue.get_nowait()
        if 'armed' in config:
            responses.append(m)
    except queue.Empty:
        pass
    
    if len(responses) > 0:
        #save responses for next cycle
        temp_file = open(TEMP_MESSAGE_FILE, 'w')
        json.dump(responses, temp_file)
        temp_file.close()