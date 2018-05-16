#!/usr/bin/env python
# encoding: utf-8

import threading
import time
import sys
#from RCPContext.RCPContext import RCPContext
from OrientalMotor import OrientalMotor
from Gripper import Gripper
from MaxonMotor import MaxonMotor
from InfraredReflectiveSensor import InfraredReflectiveSensor


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
	
        self.infraredReflectiveSensor = InfraredReflectiveSensor()
                
        self.dispatchTask = threading.Thread(None, self.listening)
        #self.dispatchTask.start()
        self.cptt = 0;
	self.global_state = 0
        
    def set_global_state(self, state):
	self.global_state = state	

    def listening(self):
        while self.flag:            
            if not self.context.get_system_status():
		self.guidewireRotateMotor.close_device()
		self.guidewireProgressMotor.close_device()
		self.catheterMotor.close_device()
		self.angioMotor.close_device()
		sys.exit()
		self.flag = False

		print "system terminated"	
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
                return
            elif msg.get_motor_orientation() == 1:
                self.catheterMotor.set_speed(-msg.get_motor_speed())
                return

	if not self.needToRetract:
            if self.context.get_guidewire_progress_instruction_sequence_length() > 0:
		self.set_global_state(self.infraredReflectiveSensor.read_current_state())
		if self.global_state == 0:
               	    msg = self.context.fetch_latest_guidewire_progress_move_msg()
	   	    if self.draw_back_guidewire_curcuit_flag == False:
                        return 
           	    if msg.get_motor_orientation() == 0 and abs(msg.get_motor_speed()) < 40*2*60:
			#print -msg.get_motor_speed()
	      	        self.guidewireProgressMotor.set_speed(-msg.get_motor_speed())
              	        self.cptt = 0
                    elif msg.get_motor_orientation() == 1 and abs(msg.get_motor_speed()) < 40*2*60:
			#print msg.get_motor_speed()
                        self.guidewireProgressMotor.set_speed(msg.get_motor_speed())
		    else:
			self.guidewireProgressMotor.set_speed(0)
	        elif self.global_state == 2:
		    #print "retract"
		    self.guidewireProgressMotor.set_speed(0)
		    self.needToRetract = True
		    retractTask = threading.Thread(None, self.draw_back_guidewire_curcuit)
       		    retractTask.start()
		elif self.global_state == 1:
		    #print "hehe", self.global_guidewire_distance
		    self.guidewireProgressMotor.set_speed(100)
		elif self.global_state == 3:
		    self.guidewireProgressMotor.set_speed(0)

       	    if self.context.get_guidewire_rotate_instruction_sequence_length() > 0:
                msg = self.context.fetch_latest_guidewire_rotate_move_msg()
                speed = msg.get_motor_speed()
                position = (msg.get_motor_position()*4000)/360
                if self.draw_back_guidewire_curcuit_flag == False:
                    return             
                if msg.get_motor_orientation() == 0:
                    self.guidewireRotateMotor.rm_move(speed)
                    pass
                elif msg.get_motor_orientation() == 1:
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
	   
	    if msg.get_volume() < 18:		
	    	self.angioMotor.set_pos_speed(msg.get_speed())
	   	self.angioMotor.set_position(msg.get_volume())
	    	self.angioMotor.push_contrast_media()
	    elif msg.get_volume() == 500.0:
		self.angioMotor.pull_back()

    def push_guidewire_back(self):
        #self.context.clear()
        self.draw_back_guidewire_curcuit_flag == False
        
	#self.gripperFront.gripper_chuck_loosen()
        #self.gripperBack.gripper_chuck_loosen()
        #time.sleep(1)	    
        
	# fasten front gripper
	self.gripperFront.gripper_chuck_fasten()
	
	# self-tightening chunck
        self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)    
        self.guidewireRotateMotor.rm_move_to_position(90, 4000) # +/loosen
        time.sleep(3)

        #self.gripperFront.gripper_chuck_loosen()
        #time.sleep(1)
	self.guidewireProgressMotor.set_speed(-800)
            
	self.global_state = self.infraredReflectiveSensor.read_current_state()
	while self.global_state != 1:
	    time.sleep(0.5)
	    self.global_state = self.infraredReflectiveSensor.read_current_state()
	    print "retracting", self.global_state
	    print "back limitation arrived"

        self.guidewireProgressMotor.set_speed(0)
        self.guidewireRotateMotor.rm_move_to_position(90, -4000)
        time.sleep(3)
  
        self.gripperFront.gripper_chuck_loosen()
        self.gripperBack.gripper_chuck_loosen()
        self.draw_back_guidewire_curcuit_flag == True
	self.needToRetract = False

    def push_guidewire(self):
#       self.context.clear()
        self.draw_back_guidewire_curcuit_flag == False
        for i in range(0, 2):
		self.gripperFront.gripper_chuck_loosen()
                self.gripperBack.gripper_chuck_loosen()
                time.sleep(1)
                self.gripperFront.gripper_chuck_fasten()
                self.gripperBack.gripper_chuck_fasten()
                time.sleep(1)

                self.guidewireRotateMotor.rm_move_to_position(40, 5000) # +/loosen
                time.sleep(8)
                self.gripperFront.gripper_chuck_loosen()

		self.global_guidewire_distance = self.ultraSoundModule.read_current_distance()
                self.guidewireProgressMotor.set_speed(600)
		while self.global_guidewire_distance > (self.frontLimitDistance + 2):
                    time.sleep(0.5)
                    self.global_guidewire_distance = self.ultraSoundModule.read_current_distance()
                    print "pushing"
                print "pushing limitation arrived"
                #time.sleep(15)
                self.guidewireProgressMotor.set_speed(0)
                time.sleep(1)
		
		self.gripperFront.gripper_chuck_loosen()
                self.gripperBack.gripper_chuck_loosen()
                time.sleep(1)
                self.gripperFront.gripper_chuck_fasten()
                self.gripperBack.gripper_chuck_fasten()
                time.sleep(1)
                self.guidewireRotateMotor.rm_move_to_position(40, -8000)
                time.sleep(8)                
		self.gripperFront.gripper_chuck_loosen()
		#time.sleep(1)
		self.guidewireProgressMotor.set_speed(-600)
		while self.global_guidewire_distance < (self.behindLimitDistance - 2):
                    time.sleep(0.5)
                    self.global_guidewire_distance = self.ultraSoundModule.read_current_distance()
                    print "fetching"
                print "fetch limitation arrived"
                #self.guidewireProgressMotor.set_speed(-400)
                #time.sleep(15)
                self.guidewireProgressMotor.set_speed(0)
                time.sleep(1)
                self.draw_back_guidewire_curcuit_flag == True
   
    def push_guidewire_advance(self):
    	self.guidewireProgressMotor.set_speed(800)
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state !=2:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
        #print "pushing", self.global_state
        #print "front limitation arrived"

        self.guidewireProgressMotor.set_speed(0)
        #self.guidewireRotateMotor.rm_move_to_position(90, -8000)   
        #time.sleep(4)
     
    def multitime_push_guidewire(self):
        for i in range (0,8):
            dispatcher.push_guidewire_advance()
            dispatcher.push_guidewire_back()
            print(i)
   
    def draw_guidewire_back(self):
        #self.draw_back_guidewire_curcuit_flag == False
        #self.gripperFront.gripper_chuck_loosen()
        #self.gripperBack.gripper_chuck_fasten()
        #time.sleep(1)
        #self.guidewireRotateMotor.rm_move_to_position(85,4000)
        #time.sleep(3)	
      
        self.guidewireProgressMotor.set_speed(-800)
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state != 1:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
            #print "retracting", self.global_state
        #print "back limitation arrived"

        self.guidewireProgressMotor.set_speed(0)
        #self.guidewireRotateMotor.rm_move_to_position(85, -4000)
        #time.sleep(4)
        #self.draw_back_guidewire_curcuit_flag == True
        #self.needToRetract = False
       
    def draw_guidewire_advance(self):
        self.gripperFront.gripper_chuck_loosen()
        self.gripperBack.gripper_chuck_loosen()
	time.sleep(1)
        self.gripperFront.gripper_chuck_fasten()
        self.gripperBack.gripper_chuck_fasten()
	time.sleep(1)
        self.guidewireRotateMotor.rm_move_to_position(80,4000)
	time.sleep(3)
	self.guidewireProgressMotor.set_speed(800)
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state !=2:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
        #print "advancing", self.global_state
        #print "front limitation arrived"
       
        self.guidewireProgressMotor.set_speed(0)
        #self.gripperFront.gripper_chuck_fasten()
        #self.gripperBack.gripper_chuck_fasten()
	time.sleep(1)
        self.guidewireRotateMotor.rm_move_to_position(80, -4000)
        time.sleep(3)
       
       # self.gripperFront.gripper_chuck_fasten()
       # time.sleep(1)
	#self.gripperFront.gripper_chuck_loosen()
        self.gripperBack.gripper_chuck_loosen()
	time.sleep(1)
         
         
    def multitime_draw_back_guidewire(self):
        for i in range (0,8):
            dispatcher.draw_guidewire_advance()
            dispatcher.draw_guidewire_back()
            print(i)
    
    def automatic_procedure(self):
        self.angioMotor.set_pos_speed(2)
        self.angioMotor.set_position(5)
        self.angioMotor.push_contrast_media()
        print "angiographing finish"
        time.sleep(5)
        self.multitime_push_guidewire()
        self.multitime_draw_back_guidewire()


    def push_and_pull(self):
        self.multitime_push_guidewire()
        self.multitime_draw_back_guidewire()

    def loosen(self):
	self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)
        self.gripperBack.gripper_chuck_loosen()
       #self.gripperBack.gripper_chuck_loosen()
        time.sleep(1)        


import sys        
dispatcher =  Dispatcher(1)
#dispatcher.push_and_pull()

#dispatcher.guidewireRotateMotor.rm_move_to_position(80, -4000)

#dispatcher.multitime_draw_back_guidewire()
#dispatcher.loosen()

#dispatcher.shiftboard_advance()
dispatcher.automatic_procedure()
#dispatcher.multitime_draw_back_guidewire()
#dispatcher.shiftboard_advance()
#dispatcher.draw_back_guidewire_pull()
#dispatcher.shiftboard_advance()


#dispatcher.draw_back_guidewire_curcuit()
#dispatcher =  Dispatcher(1)
#self.gripperFront.gripper_chuck_loosen()

#dispatcher.guidewireProgressMotor.set_speed(-400)
#time.sleep(10)
#dispatcher.guidewireProgressMotor.set_speed(0)
#from Dispatcher import Dispatcher
#dispatcher =  Dispatcher(1)
#dispatcher.multitime_push_guidewire()
