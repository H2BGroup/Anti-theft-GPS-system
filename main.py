# from receiveSMS import receiveSMS
from rabbit import checkRabbit, setupPPP
from location import setupGPS, power_down, power_key
import time
import os
from accelerometer import Accelerometer_Thread
from queue import Queue

SCAN_EVERY = 5 #seconds
PAUSE_DURATION = 1

def main():
    # make sure internet if off so gps can setup properly
    os.system("sudo poff rnet")
    while os.system("ip link show | grep ppp0 > /dev/null") == 0:
        time.sleep(0.5)

    GPS_on = setupGPS()
    if GPS_on != True:
        print("ERROR Couldn't start GPS")
        return
    setupPPP()
    acc_queue = Queue()
    acc = Accelerometer_Thread(acc_queue)
    acc.start_accelerometer()
    try:
        while True:
            print("Check internet")
            checkRabbit(acc_queue)
            time.sleep(SCAN_EVERY)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up before exiting")
        power_down(power_key)
    finally:
        print("Exiting")


if __name__ == "__main__":
    main()