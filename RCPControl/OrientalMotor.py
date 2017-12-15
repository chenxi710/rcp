#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading


class OrientalMotor(object):
    def __init__(self, push_io, pull_io):
        
        self.orientalMotorPushLock = threading.Lock()
        self.orientalMotorPullLock = threading.Lock()
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.flag = True
        self.speedFlag = 0
        self.count = 0
        self.pushIO = push_io
        self.pullIO = pull_io
        GPIO.setup(self.pushIO, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.pullIO, GPIO.OUT, initial=GPIO.HIGH)

        #velocity mode
        self.speed = 1
        self.moveTask = threading.Thread(None, self.continious_move)
        self.moveTask.start()

        #position mode
        self.pos_motor_flag = 1
        self.position = 0
        self.pos_speed = 60

    def close_device(self):
	self.flag = False

    def set_speed(self, speed):
        if speed > 0:
            self.speedFlag = 1
        elif speed < 0:
            self.speedFlag = 2
        self.speed = abs(speed)
        
        if speed == 0:
            self.speed = 1
        
    def continious_move(self):
        while self.flag:
            
            if self.speed in range(0, 20):
                time.sleep(0.1)
                continue
            
            if self.speedFlag == 1:
                self.push()
            
            if self.speedFlag == 2:
                self.pull()
            

    def rtz(self):
        GPIO.output(self.pushIO, True)
        GPIO.output(self.pullIO, True)
    
    def push(self):
        self.orientalMotorPushLock.acquire()
        GPIO.output(self.pushIO, False)              
        time.sleep(0.0005*60/self.speed)                
        GPIO.output(self.pushIO, True)
        time.sleep(0.0005*60/self.speed)
        self.count += 1
        self.orientalMotorPushLock.release()

    def pull(self):
        GPIO.output(self.pullIO, False)
        time.sleep(0.0005*60/self.speed)
        GPIO.output(self.pullIO, True)
        time.sleep(0.0005*60/self.speed) 
        self.count += 1

    #Position Mode
    
    def set_position(self, position):
        self.position = position

    def set_pos_speed(self, pos_speed):
        self.pos_speed = pos_speed
        
##    def continious_move_position(self):
##        while self.flag:
##            if self.speed in range(-1, 1):
##                time.sleep(0.1)
##                continue
##            
##            if self.speed > 1:
##                    
##                self.push()
##            elif self.speed < -1:
##                self.pull()

    def idt_motor(self):    #identify the motor type
        #if advancement motor, pos_motor_flag=4;
        if self.pushIO == 2 and self.pullIO == 3:
            self.pos_motor_flag = 4

        #if catheterMotor, pos_motor_flag=??
        if self.pushIO == 14 and self.pullIO == 15:
            self.pos_motor_flag = 1

        #if angioMotor, pos_motor_flag=??
        if self.pushIO == 23 and self.pullIO == 24:
            self.pos_motor_flag = 1

    def position_move(self):
        if self.position in range(-1, 1):
            time.sleep(0.1)
        
        if self.position > 1:            
            self.position_push()
            
        elif self.position < -1:
            self.position_pull()

    
    def position_push(self):
        self.idt_motor()
        for i in range(0, 1000*self.position/self.pos_motor_flag): 
            GPIO.output(self.pushIO, False)              
            time.sleep(0.0005*60/self.pos_speed)                
            GPIO.output(self.pushIO, True)
            time.sleep(0.0005*60/self.pos_speed)
            self.count += 1
            
    def position_pull(self):
        self.idt_motor()
        for i in range(0, 1000*-self.position/self.pos_motor_flag):
            GPIO.output(self.pullIO, False)              
            time.sleep(0.0005*60/self.pos_speed)             
            GPIO.output(self.pullIO, True)
            time.sleep(0.0005*60/self.pos_speed)
            self.count += 1

#motor = OrientalMotor(20, 21)
#motor.set_speed(-300)
#time.sleep(5)
#motor.set_speed(0)
