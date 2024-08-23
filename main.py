from receiveSMS import receiveSMS
from rabbit import checkRabbit
import time
import gammu

SCAN_EVERY = 10 #seconds
PAUSE_DURATION = 1

def main():

    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()

    try:
        while True:
            print("Check sms")
            receiveSMS(state_machine)
            time.sleep(PAUSE_DURATION)
            print("Check internet")
            checkRabbit()
            time.sleep(SCAN_EVERY)
    except KeyboardInterrupt:
        print("Interrupted, cleaning up before exiting")
        state_machine.Terminate()
    finally:
        print("Exiting")


if __name__ == "__main__":
    main()