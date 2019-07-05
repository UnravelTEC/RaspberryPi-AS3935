#!/usr/bin/env python
from RPi_AS3935 import RPi_AS3935

import RPi.GPIO as GPIO
import time
from datetime import datetime
from subprocess import call

SENSOR_FOLDER = '/run/sensors/'
SENSOR_NAME = 'as3935'
LOGFILE = SENSOR_FOLDER + SENSOR_NAME + '/last'

call(["mkdir", "-p", SENSOR_FOLDER + SENSOR_NAME])

GPIO.setmode(GPIO.BCM)

# Rev. 1 Raspberry Pis should leave bus set at 0, while rev. 2 Pis should set
# bus equal to 1. The address should be changed to match the address of the
# sensor. (Common implementations are in README.md)
sensor = RPi_AS3935(address=0x03, bus=1)

sensor.set_indoors(True)
sensor.set_noise_floor(0)
sensor.calibrate(tun_cap=0x0F)


def handle_interrupt(channel):
    now = datetime.now().strftime('%H:%M:%S - %Y/%m/%d')
    time.sleep(0.003)
    global sensor
    reason = sensor.get_interrupt()
    if reason == 0x01:
        print "%s Noise level too high - adjusting" % now
        sensor.raise_noise_floor()
    elif reason == 0x04:
        print "%s Disturber detected - masking" % now
        sensor.set_mask_disturber(True)
    elif reason == 0x08:
        distance = sensor.get_distance()
        print "We sensed lightning!"
        print "It was " + str(distance) + "km away. (%s)" % now
        print ""
        output_string =  'emp_distance_km{sensor="AS3935"} ' + str(distance) + '\n'
        logfilehandle = open(LOGFILE, "w",1)
        logfilehandle.write(output_string)
        logfilehandle.close()

pin = 17

GPIO.setup(pin, GPIO.IN)
GPIO.add_event_detect(pin, GPIO.RISING, callback=handle_interrupt)

now = datetime.now().strftime('%H:%M:%S - %Y/%m/%d')
print "%s Waiting for lightning - or at least something that looks like it" % now

output_string =  'emp_distance_km{sensor="AS3935"} 42\n' 
logfilehandle = open(LOGFILE, "w",1)
logfilehandle.write(output_string)
logfilehandle.close()

while True:
    time.sleep(10)
    now = datetime.now().strftime('%H:%M:%S - %Y/%m/%d')
    distance = sensor.get_distance()
    if distance != False:
      print "last distance " + str(distance) + "km away. (%s)" % now
    #else:
    #  print "nothing new at %s" % now
