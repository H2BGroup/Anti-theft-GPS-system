from receiveSMS import receiveSMS
from rabbit import checkRabbit
from location import setupGPS, power_down
import time

SCAN_EVERY = 10 #seconds
PAUSE_DURATION = 1

def main():
    setupGPS()
    try:
        while True:
            print("Check sms")
            receiveSMS()
            time.sleep(PAUSE_DURATION)
            print("Check internet")
            checkRabbit()
            time.sleep(SCAN_EVERY)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up before exiting")
        power_down()
    finally:
        print("Exiting")


if __name__ == "__main__":
    main()