#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading
import random


class InfraredReflectiveSensor(object):
    def __init__(self):
        self.doutBack = 2
	self.doutFront = 3
	self.flag = True
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	GPIO.setup(self.doutBack, GPIO.IN)
	GPIO.setup(self.doutFront, GPIO.IN)
    
    def read_current_state(self):
	back = GPIO.input(self.doutBack)
        front = GPIO.input(self.doutFront)
	

#	print "front", front,"back", back
        if back == 0 and front == 1:
            return 1
        if back == 1 and front == 0:
            return 2
	if back == 0 and front == 0:
	    return 3
	return 0

    def read(self):
        cpt = 0
        while self.flag:
    	    self.read_current_state()
       	    time.sleep(0.5)

#irs = InfraredReflectiveSensor()
#irs.read()
