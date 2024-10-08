#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import serial
import time
from datetime import datetime

power_key = 4
MAX_RETRIES = 10

def send_at(ser, command, back, timeout):
    ser.write((command + '\r\n').encode())
    print(f'Sent: {command}')
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01)
        rec_buff = ser.read(ser.inWaiting())
        if rec_buff:
            response = rec_buff.decode()
            print(f'Response: {response}')
            if back not in response:
                print(f'{command} ERROR')
                return None
            else:
                return response
    print('No response or GPS is not ready')
    return None

def get_gps_position(ser):
    retries = 0
    
    while True:
        if retries >= MAX_RETRIES:
            return None, None, None
        response = send_at(ser, 'AT+CGNSINF', '+CGNSINF: ', 1)
        if response:
            if ',,,,,,' not in response:
                gps_data = response.split(',')
                if len(gps_data) >= 4:
                    utc_time = gps_data[2].split('.')[0]  # Remove the fraction of a second part
                    latitude = gps_data[3]
                    longitude = gps_data[4]
                    if utc_time:
                        utc_time = datetime.strptime(utc_time, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                    print(f"UTC time is: {utc_time}")
                    print(f"Latitude is: {latitude}")
                    print(f"Longitude is: {longitude}")
                    return utc_time, latitude, longitude
            else:
                print('GPS is not ready, retrying...')
                time.sleep(1.5)
                retries += 1
        else:
            print('Error in getting GPS data, retrying...')
            time.sleep(1.5)
            retries += 1

def power_on(ser, power_key):
    print('SIM7600X is starting:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key, GPIO.LOW)
    time.sleep(2)
    ser.flushInput()
    print('SIM7600X is ready')

def power_down(power_key):
    print('SIM7600X is logging off:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key, GPIO.LOW)
    time.sleep(2)
    GPIO.cleanup()
    print('Good bye')

def setupGPS():
    ser = serial.Serial('/dev/ttyS0', 115200)
    ser.flushInput()
    power_down(power_key)
    power_on(ser, power_key)

    print('Start GPS session...')
    success = False
    tries = 0
    while tries <= MAX_RETRIES:
        tries += 1
        response = send_at(ser, 'AT+CGNSPWR=1', 'OK', 1)
        if response != None:
            success = True
            break    
    
    time.sleep(1)

    ser.close()
    ser=None
    GPIO.cleanup()

    return success

def getLocation():
    utc_time = None
    latitude = None
    longitude = None
    
    try:
        ser = serial.Serial('/dev/ttyS0', 115200)
        ser.flushInput()
        # power_on(ser, power_key)
        utc_time, latitude, longitude = get_gps_position(ser)
        # power_down(power_key)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if ser:
            ser.close()
        GPIO.cleanup()
    if utc_time == None or latitude == None or longitude == None:
        return None, None, None
    
    return latitude, longitude, utc_time