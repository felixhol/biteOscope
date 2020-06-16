'''
author: Felix Hol
date: some time in 2018
content: temperature control using a ds1820 temperature probe, a relay and peltier element (running on raspberry pi)
depending on temperature reading, GPIO pins switch relay to heat peltier
'''


import os
import glob
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c#, temp_f

while True:
        print(read_temp())
        if read_temp() < 37:
                GPIO.output(12, GPIO.LOW)
                print('heating')
                time.sleep(1)
                GPIO.output(12, GPIO.HIGH)
                print('stop heating')
        else:
                GPIO.output(12, GPIO.HIGH)
                time.sleep(1)

