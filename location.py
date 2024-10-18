#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import serial
import time
from datetime import datetime, timezone

power_key = 4
MAX_RETRIES = 5

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

def lat_to_decimal(s):
    dd = float(s[:2])
    mm = float(s[2:]) / 60
    return dd + mm

def lon_to_decimal(s):
    ddd = float(s[:3])
    mm = float(s[3:]) / 60
    return ddd + mm

def get_gps_position_NMEA():
    latitude = None
    longitude = None
    utc_time = None

    with serial.Serial('/dev/ttyUSB1', 115200, timeout=5, rtscts=True, dsrdtr=True) as ser:
        if ser.readable() != True:
            raise Exception("Serial port not readable")
        data = ser.read(1000).decode()
        lines = data.split('\r\n')
        for line in lines:
            if 'RMC' in line: # we need only recommended minimum navigation
                print(line)
                line_fields = line.split(',')
                valid = line_fields[2]
                lat = line_fields[3]
                lat_dir = line_fields[4]
                lon = line_fields[5]
                lon_dir = line_fields[6]

                if valid != 'A':
                    raise Exception("Invalid GPS data. GPS module might not be ready.")
                if lat == '' or lon == '':
                    break
                
                latitude = lat_to_decimal(lat)
                longitude = lon_to_decimal(lon)

                if lat_dir == 'S':
                    latitude *= -1
                if lon_dir == 'W':
                    longitude *= -1

                utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

                break
    
    return latitude, longitude, utc_time
    

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
        response_mode = send_at(ser, 'AT+CGNSCFG=1', 'OK', 1)
        response_PWR = send_at(ser, 'AT+CGNSPWR=1', 'OK', 1)
        if response_mode != None and response_PWR != None:
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
        latitude, longitude, utc_time = get_gps_position_NMEA()         
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return latitude, longitude, utc_time