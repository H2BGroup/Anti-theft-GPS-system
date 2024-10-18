from gpiozero import TonalBuzzer
from gpiozero.tools import sin_values, absoluted
from time import sleep
from threading import Thread

def sound_alarm():
    b = TonalBuzzer(26)

    b.source_delay = 0.01
    b.source = absoluted(sin_values(100))
    sleep(10)
    b.source = None
    b = None