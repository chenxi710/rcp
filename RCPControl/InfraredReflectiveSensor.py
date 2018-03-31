#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading
import random


class InfraredReflectiveSensor(object):
    def __init__(self):
        self.DOUTOne = 2
	self.DOUTTwo = 3
	self.flag = True
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(self.DOUTOne, GPIO.IN)
	GPIO.setup(self.DOUTTwo, GPIO.IN)
    
    def read_current_state(self):
	dataOne = GPIO.input(self.DOUTOne)
        dataTwo = GPIO.input(self.DOUTTwo)
        if dataOne == 0 and dataTwo == 1:
            return 1
        if dataOne == 1 and dataTwo == 0:
            return 2
	if dataOne == 1 and dataTwo == 1:
	    return 3
	return 0

    #def read(self):
    #    cpt = 0
    #    while self.flag:
    #	    print self.read_current_state()
    #   	    time.sleep(0.5)

#irs = InfraredReflectiveSensor()
#irs.read()
