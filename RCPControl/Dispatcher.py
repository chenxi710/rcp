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
        self.draw_back_guidewire_curcuit_flag = True
        self.guidewireProgressMotor = OrientalMotor(20, 21)
        self.guidewireRotateMotor = MaxonMotor(2, "EPOS2", "MAXON SERIAL V2", "USB", "USB0", 1000000)
        self.catheterMotor = OrientalMotor(14, 15)
        self.angioMotor = OrientalMotor(23, 24)

        self.gripperFront = Gripper(7)
        self.gripperBack = Gripper(8)

        #self.ultraSoundModule = UltraSoundModule(context)
                
        self.dispatchTask = threading.Thread(None, self.listening)
        self.dispatchTask.start()
        self.cptt = 0;
        
    def listening(self):
        while self.flag:
            
            if not self.context.get_system_status():
		self.guidewireRotateMotor.close_device()
		self.guidewireProgressMotor.close_device()
		self.catheterMotor.close_device()
		self.angioMotor.close_device()
		self.flag = False	
	    else:
	    	self.decode()	

	    time.sleep(0.05)
	    

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

        if self.context.get_guidewire_progress_instruction_sequence_length() > 0:
            msg = self.context.fetch_latest_guidewire_progress_move_msg()
	    if self.draw_back_guidewire_curcuit_flag == False:
                return 
            if msg.get_motor_orientation() == 0:
	       self.guidewireProgressMotor.set_speed(-msg.get_motor_speed())
               self.cptt = 0
            elif msg.get_motor_orientation() == 1:
               self.guidewireProgressMotor.set_speed(msg.get_motor_speed())

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
