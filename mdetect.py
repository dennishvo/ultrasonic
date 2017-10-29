#!/usr/bin/python
#
# mdetect.py
# 
# Measure distance using an ultrasonic module
# Use std deviation calc to detect good readings and 
# to throw out bad readings 
#
# Created by      : Dennis Kornbluh
# Date            : 08/11/2017
# -----------------------

# Import required Python libraries
from __future__ import print_function
import time
import RPi.GPIO as GPIO
import math

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_TRIGGER = 23
GPIO_ECHO    = 24

# Speed of sound in cm/s at temperature
temperature = 20
speedSound = 33100 + (0.6*temperature)

def computeStdDev(list):
	mn = mean(list) 
	newList = []
	for val in list:
		tmp = val - mn
		tmp *= tmp
		newList.append(tmp)
	mn = mean(newList)
	stddev = math.sqrt(mn) 
	return stddev
	
def mean(list):
	mn = 0.0
	for val in list:
		mn += val
	mn = mn / len(list)
	return mn

print("Ultrasonic Measurement")
print("Speed of sound is",speedSound/100,"m/s at ",temperature,"deg")

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

CM2FT = 0.0328084
LODEV = 1.0
HIDEV = 100.0
MAX = 20
readCount = 0
list = []

try:
	while 1:
		# Set trigger to False (Low)
		GPIO.output(GPIO_TRIGGER, False)

		# Allow module to settle
		time.sleep(0.1)

		# Send 10us pulse to trigger
		GPIO.output(GPIO_TRIGGER, True)
		# Wait 10us
		time.sleep(0.00001)
		GPIO.output(GPIO_TRIGGER, False)
		start = time.time()

		while GPIO.input(GPIO_ECHO)==0:
  			start = time.time()

		while GPIO.input(GPIO_ECHO)==1:
  			stop = time.time()

		# Calculate pulse length
		elapsed = stop-start

		# Distance pulse travelled in that time is time
		# multiplied by the speed of sound (cm/s)
		distance = elapsed * speedSound

		# That was the distance there and back so halve the value
		distance = distance / 2

		# Store MAX readings, compute std deviation
		list.append(distance)
		readCount += 1

		if readCount >= MAX:
			readCount = 0
			stddev = computeStdDev(list)
			list = []
			if stddev > LODEV and stddev <= HIDEV:
				print("Something is moving. Distance={0:5.1f} cm, {1:5.2f} ft. StdDev={2:5.2f}".format(distance,distance*CM2FT,stddev))
			elif stddev > HIDEV:
				print("High deviation:{0:5.2f}".format(stddev))
except KeyboardInterrupt:
	print("Quitting")

# Reset GPIO settings
GPIO.cleanup()
