from receiveSMS import receiveSMS
from rabbit import checkRabbit
import time

SCAN_EVERY = 10 #seconds
PAUSE_DURATION = 1

def main():

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
    finally:
        print("Exiting")


if __name__ == "__main__":
    main()