from activity_detect.activity_detect import Accelerometer
from threading import Thread
from queue import Queue
from datetime import datetime, timezone
from buzzer import sound_alarm
import json

CONFIG_FILE = '/usr/local/sbin/Anti-theft-GPS-system/config.json'

class Accelerometer_Thread:

    def __init__(self, queue: Queue):
        self.message_queue = queue

    def start_accelerometer(self):
        accelerometer = Accelerometer(self.movement_detected)
        Thread(target=accelerometer.run).start()

    def movement_detected(self):
        if self.message_queue.qsize() == 0:
            print("Acc queue empty. Inserting message")
            self.message_queue.put({
                'type': 'movement_detected',
                'utc_time': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            })

            f = open(CONFIG_FILE)
            config = json.load(f)
            f.close()
            if 'armed' in config and config['armed'] == True:
                print("Device armed sounding alarm!") 
                sound_alarm()