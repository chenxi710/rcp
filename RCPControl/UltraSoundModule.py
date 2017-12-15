#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading


class UltraSoundModule(object):
    def __init__(self, context):
	self.context = context

	self.flag = True
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.Trig = 2
        self.Echo = 3
        GPIO.setup(self.Trig, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(self.Echo, GPIO.IN)
	self.moveTask = threading.Thread(None, self.read)
       	#self.moveTask.start()
				
    def read(self):
	cpt = 0
        while self.flag:
		GPIO.output(self.Trig, True)
		time.sleep(0.00001)
		GPIO.output(self.Trig, False)
		while GPIO.input(self.Echo) == 0:
			pass
		start = time.time()
		while GPIO.input(self.Echo) == 1:
			pass
		end = time.time()
			
		distance = round(((end-start)*340*100/2),2)
			
		time.sleep(0.5)
		#print distance
		self.context.set_distance(distance)
		cpt += 1

#x = UltraSoundModule(0)	
