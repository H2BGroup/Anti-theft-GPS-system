from receiveSMS import receiveSMS
from rabbit import checkRabbit
from location import setupGPS, power_down, power_key
import time
import os

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
    try:
        while True:
            print("Check internet")
            checkRabbit()
            time.sleep(PAUSE_DURATION)
            print("Check sms")
            receiveSMS()
            time.sleep(SCAN_EVERY)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up before exiting")
        power_down(power_key)
    finally:
        print("Exiting")


if __name__ == "__main__":
    main()