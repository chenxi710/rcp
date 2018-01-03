#!/usr/bin/env python
# encoding: utf-8

import threading
import time
from RCPContext.RCPContext import RCPContext
from OrientalMotor import OrientalMotor
from Gripper import Gripper
from MaxonMotor import MaxonMotor
from UltraSoundModule import UltraSoundModule


class Dispatcher(object):
    def __init__(self, context):
        self.context = context
        self.flag = True
	self.needToRetract = False
        self.draw_back_guidewire_curcuit_flag = True
        self.guidewireProgressMotor = OrientalMotor(20, 21, True)
        self.guidewireRotateMotor = MaxonMotor(2, "EPOS2", "MAXON SERIAL V2", "USB", "USB0", 1000000)
        self.catheterMotor = OrientalMotor(14, 15, True)
        self.angioMotor = OrientalMotor(23, 24, False)

        self.gripperFront = Gripper(7)
        self.gripperBack = Gripper(8)

        self.ultraSoundModule = UltraSoundModule(self, context)
                
        self.dispatchTask = threading.Thread(None, self.listening)
        self.dispatchTask.start()
        self.cptt = 0;
	self.global_guidewire_distance = 27.0
        
    def set_global_guidewire_distance(self, distance):
	self.global_guidewire_distance = distance	

    def listening(self):
        while self.flag:
            
            if not self.context.get_system_status():
		self.guidewireRotateMotor.close_device()
		self.guidewireProgressMotor.close_device()
		self.catheterMotor.close_device()
		self.angioMotor.close_device()
		self.flag = False

		print "system terminated"	
	    else:
	    	self.decode()	

	    time.sleep(0.1)
	    

    def decode(self):

        if self.context.get_catheter_move_instruction_sequence_length() > 0:
            msg = self.context.fetch_latest_catheter_move_msg()
            if self.draw_back_guidewire_curcuit_flag == False:
                return 
            if msg.get_motor_orientation() == 0:
                self.catheterMotor.set_speed(msg.get_motor_speed())
                pass
            elif msg.get_motor_orientation() == 1:
                self.catheterMotor.set_speed(-msg.get_motor_speed())
                pass

	if not self.needToRetract:
            if self.context.get_guidewire_progress_instruction_sequence_length() > 0:
	        if (self.global_guidewire_distance > 11.0) and (self.global_guidewire_distance < 26.0):
               	    msg = self.context.fetch_latest_guidewire_progress_move_msg()
	   	    if self.draw_back_guidewire_curcuit_flag == False:
                        return 
           	    if msg.get_motor_orientation() == 0:
	      	        self.guidewireProgressMotor.set_speed(-msg.get_motor_speed())
              	        self.cptt = 0
                    elif msg.get_motor_orientation() == 1:
                        self.guidewireProgressMotor.set_speed(msg.get_motor_speed())
	        else:
		    self.needToRetract = True
		    retractTask = threading.Thread(None, self.draw_back_guidewire_curcuit)
       		    retractTask.start()

        if self.context.get_guidewire_rotate_instruction_sequence_length() > 0:
            msg = self.context.fetch_latest_guidewire_rotate_move_msg()
            speed = msg.get_motor_speed()
            position = (msg.get_motor_position()*2000)/360
            if self.draw_back_guidewire_curcuit_flag == False:
                return             
            if msg.get_motor_orientation() == 0:
#                print "speed----------0", speed, position
                self.guidewireRotateMotor.rm_move(speed)
                pass
            elif msg.get_motor_orientation() == 1:
#                print "speed----------1", speed, position
                self.guidewireRotateMotor.rm_move(-speed)
                pass

        if self.context.get_contrast_media_push_instruction_sequence_length() > 0:
            msg = self.context.fetch_latest_contrast_media_push_move_msg()
            ret = msg.get_motor_speed()
            if self.draw_back_guidewire_curcuit_flag == False:
                return 
            if msg.get_motor_orientation() == 0:
                self.angioMotor.set_speed(-ret)
            elif msg.get_motor_orientation() == 1:
                self.angioMotor.set_speed(ret)

        if self.context.get_retract_instruction_sequence_length() > 0:
            if self.draw_back_guidewire_curcuit_flag == False:
                return 
            self.draw_back_guidewire_curcuit()

	if self.context.get_injection_command_sequence_length() > 0:
	    msg = self.context.fetch_latest_injection_msg_msg()
            #print "injection command", msg.get_speed(),msg.get_volume()
	    if msg.get_volume() < 10:		
	    	self.angioMotor.set_pos_speed(msg.get_speed())
	   	self.angioMotor.set_position(msg.get_volume())
	    	self.angioMotor.push_contrast_media()
	    elif msg.get_volume() == 50.0:
		self.angioMotor.pull_back()

    def draw_back_guidewire_curcuit(self):
            self.context.clear()
            self.draw_back_guidewire_curcuit_flag == False
            self.gripperFront.gripper_chuck_loosen()
            self.gripperBack.gripper_chuck_loosen()
            time.sleep(1)
            self.gripperFront.gripper_chuck_fasten()
            self.gripperBack.gripper_chuck_fasten()
            time.sleep(1)
            
            self.guidewireRotateMotor.rm_move_to_position(40, 8000) # +/loosen
            time.sleep(8)
            self.gripperFront.gripper_chuck_loosen()
            self.guidewireProgressMotor.set_speed(-400)
            time.sleep(15)
            self.guidewireProgressMotor.set_speed(1)
            self.gripperFront.gripper_chuck_loosen()
            self.gripperBack.gripper_chuck_loosen()
            time.sleep(1)
            self.gripperFront.gripper_chuck_fasten()
            self.gripperBack.gripper_chuck_fasten()
            time.sleep(1)
            self.guidewireRotateMotor.rm_move_to_position(40, -8000)
            time.sleep(8)
            self.guidewireProgressMotor.set_speed(1)
            self.gripperFront.gripper_chuck_loosen()
            self.gripperBack.gripper_chuck_loosen()
            self.draw_back_guidewire_curcuit_flag == True
	    self.needToRetract = False

    def push_guidewire(self):
#            self.context.clear()
            self.draw_back_guidewire_curcuit_flag == False
            for i in range(0, 2):
                dispatcher.guidewireProgressMotor.set_speed(400)
                time.sleep(15)
                dispatcher.guidewireProgressMotor.set_speed(0)
                time.sleep(1)
                
                self.gripperFront.gripper_chuck_loosen()
                self.gripperBack.gripper_chuck_loosen()
                time.sleep(1)
                self.gripperFront.gripper_chuck_fasten()
                self.gripperBack.gripper_chuck_fasten()
                time.sleep(1)
                
                self.guidewireRotateMotor.rm_move_to_position(40, 8000) # +/loosen
                time.sleep(8)
                self.gripperFront.gripper_chuck_loosen()
                self.guidewireProgressMotor.set_speed(-400)
                time.sleep(15)
                self.guidewireProgressMotor.set_speed(1)
                self.gripperFront.gripper_chuck_loosen()
                self.gripperBack.gripper_chuck_loosen()
                time.sleep(1)
                self.gripperFront.gripper_chuck_fasten()
                self.gripperBack.gripper_chuck_fasten()
                time.sleep(1)
                self.guidewireRotateMotor.rm_move_to_position(40, -8000)
                time.sleep(8)
                self.guidewireProgressMotor.set_speed(1)
                self.gripperFront.gripper_chuck_loosen()
                self.gripperBack.gripper_chuck_loosen()
                time.sleep(1.5)
            self.draw_back_guidewire_curcuit_flag == True
"""            
import sys        
dispatcher =  Dispatcher(1)
#dispatcher.guidewireProgressMotor.set_speed(-400)
#time.sleep(10)
#dispatcher.guidewireProgressMotor.set_speed(0)
#dispatcher.draw_back_guidewire_curcuit()
dispatcher.push_guidewire()
sys.exit() 
"""
