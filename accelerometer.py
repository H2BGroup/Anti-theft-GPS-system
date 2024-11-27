from activity_detect.activity_detect import Accelerometer
from threading import Thread
from queue import Queue
from datetime import datetime, timezone
from buzzer import sound_alarm
import json
import time

CONFIG_FILE = '/usr/local/sbin/Anti-theft-GPS-system/config.json'
ACC_ERROR_PAUSE_DURATION=5

class Accelerometer_Thread:

    def __init__(self, queue: Queue):
        self.message_queue = queue

    def thread_wrapper(self):
        while True:
            try:
                acc = Accelerometer(self.movement_detected)
                acc.run()
            except OSError:
                print("Accelerometer connection error")
                time.sleep(ACC_ERROR_PAUSE_DURATION)

    def start_accelerometer(self):
        Thread(target=self.thread_wrapper, daemon=True).start()

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