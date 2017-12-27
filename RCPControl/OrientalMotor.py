#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading


class OrientalMotor(object):
    def __init__(self, push_io, pull_io, mode_flag):
        
        self.orientalMotorPushLock = threading.Lock()
        self.orientalMotorPullLock = threading.Lock()
        self.orientalMotorPositionPushLock = threading.Lock()
	self.orientalMotorPositionPullLock = threading.Lock()

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.flag = True
	self.pos_flag = True
        self.speedFlag = 0
        self.count = 0
        self.pushIO = push_io
        self.pullIO = pull_io
        GPIO.setup(self.pushIO, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.pullIO, GPIO.OUT, initial=GPIO.HIGH)


	#mode choose
	self.mode = mode_flag

        #velocity mode
        self.speed = 0

        #position mode
        self.pos_motor_flag = 2
	self.re_vol_pos = 6.5
        self.position = 0
	self.re_volsp_possp = 30 
        self.pos_speed = 60

	if self.mode:
	    self.moveTask = threading.Thread(None, self.continuous_move)
            self.moveTask.start()
	else:
	    self.moveTask = threading.Thread(None, self.continuous_move_position)
            self.moveTask.start()


    def close_device(self):
	self.flag = False

    def close_position_device(self):
	self.pos_flag = False

    def set_speed(self, speed):
        if speed > 0:
            self.speedFlag = 1
        elif speed < 0:
            self.speedFlag = 2
#        self.speed = abs(speed)        
        elif speed == 0:
	    self.speedFlag = 0
#	    self.flag = False
#            self.speed = 1
        self.speed = abs(speed)
    
    def continuous_move(self):
        while self.flag:            
#            if self.speed in range(0, 20):
#                time.sleep(0.1)
#                continue
            if self.speedFlag == 0:
		time.sleep(0.001)

            if self.speedFlag == 1:
                self.push()
            
            if self.speedFlag == 2:
                self.pull()
	    
    def rtz(self):
        GPIO.output(self.pushIO, True)
        GPIO.output(self.pullIO, True)
    
    def push(self):
        self.orientalMotorPushLock.acquire()
#	interval = 0.0005*60/self.speed
	if self.speed == 0:
	    interval = 0
	else:
            interval = 0.0005*60/self.speed
        GPIO.output(self.pushIO, False)              
        time.sleep(interval)                
        GPIO.output(self.pushIO, True)
        time.sleep(interval)
        self.count += 1
        self.orientalMotorPushLock.release()

    def pull(self):
        self.orientalMotorPullLock.acquire()
	if self.speed == 0:
            interval = 0
        else:
            interval = 0.0005*60/self.speed
        GPIO.output(self.pullIO, False)
        time.sleep(interval)
        GPIO.output(self.pullIO, True)
        time.sleep(interval) 
        self.count += 1
        self.orientalMotorPullLock.release()


    #Position Mode    
    def set_position(self, volume):
        self.position = int(volume*self.re_vol_pos)

    def set_pos_speed(self, vol_speed):
        self.pos_speed = int(vol_speed*self.re_volsp_possp)
        
    def continuous_move_position(self):
        while self.pos_flag:                     
            if self.position > 0:                   
                self.position_push()
#		self.pos_flag = False
            elif self.position < 0:
                self.position_pull()
	    elif self.position == 0:
		time.sleep(0.001)
#		self.pos_flag = False

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
    
    def position_push(self):
	self.orientalMotorPositionPushLock.acquire()
        self.idt_motor()
        if self.position == 0 or self.pos_speed == 0:
            distance = 0
	    interval = 0
	else:
            distance = int(1000*self.position/self.pos_motor_flag)
	    interval = 0.0005*60/self.pos_speed
#	print distance
        for i in range(0, distance): 
            GPIO.output(self.pushIO, False)              
            time.sleep(interval)                
            GPIO.output(self.pushIO, True)
            time.sleep(interval)
            self.count += 1
	self.orientalMotorPositionPushLock.release()

            
    def position_pull(self):
	self.orientalMotorPositionPullLock.acquire()
        self.idt_motor()
	if self.position == 0 or self.pos_speed == 0:
            distance = 0
            interval = 0
        else:
            distance = int(-1000*self.position/self.pos_motor_flag)
            interval = 0.0005*60/self.pos_speed
#	print distance
        for i in range(0, distance):
            GPIO.output(self.pullIO, False)              
            time.sleep(interval)             
            GPIO.output(self.pullIO, True)
            time.sleep(interval)
            self.count += 1
	self.orientalMotorPositionPullLock.release()

    def get_position_sleep_time(self):
	if self.position == 0 or self.pos_speed == 0:
	    return 0.001
	else:
	    return abs(self.position*60/self.pos_motor_flag/self.pos_speed)


motor = OrientalMotor(23, 24, True)
motor.set_speed(50)
#motor.continuous_move()
time.sleep(2)
motor.set_speed(0)
#motor.continuous_move()
time.sleep(2)
motor.set_speed(-50)
#motor.continuous_move()
time.sleep(2)
#motor.set_speed(0)
motor.close_device()

motor1 = OrientalMotor(23, 24, False)
motor1.set_position(0.5)
time.sleep(motor1.get_position_sleep_time())
motor1.set_position(0)
time.sleep(motor1.get_position_sleep_time())
motor1.set_position(-0.5)
time.sleep(motor1.get_position_sleep_time())
motor1.close_position_device()
#motor.set_pos_speed(100)
#motor.position_move()
#time.sleep(1)
#motor.set_speed(0)
