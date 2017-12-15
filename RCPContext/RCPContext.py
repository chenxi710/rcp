#-*- coding: utf-8 -*-

import threading


class RCPContext:
    def __init__(self):
        self.inputLock = threading.Lock()
        self.outputLock = threading.Lock()
        
        self.catheterMoveInstructionSequence = []
        self.guidewireProgressInstructionSequence = []
        self.guidewireRotateInstructionSequence = []
        self.contrastMediaPushInstructionSequence = []

        self.retractInstructionSequence = []
	self.guidewireMovingDistance = []
	
	self.systemStatus = True

    def close_system(self):
	self.systemStatus = False
	
	self.catheterMoveInstructionSequence = []
        self.guidewireProgressInstructionSequence = []
        self.guidewireRotateInstructionSequence = []
        self.contrastMediaPushInstructionSequence = []
        self.retractInstructionSequence = []
        self.guidewireMovingDistance = []
	
    def open_system(self):
	self.systemStatus = True

    def get_system_status(self):
	return self.systemStatus

    def clear(self):
        self.catheterMoveInstructionSequence = []
        self.guidewireProgressInstructionSequence = []
        self.guidewireRotateInstructionSequence = []
        self.contrastMediaPushInstructionSequence = []

        self.retractInstructionSequence = []

    def set_distance(self, dis):
	self.guidewireMovingDistance.append(dis)

    def fetch_latest_guidewire_moving_distance(self):
	self.outputLock.acquire()
        length = len(self.guidewireMovingDistance)
        ret = self.guidewireMovingDistance[length-1]
        self.outputLock.release()
        return ret		

    def fetch_latest_guidewire_moving_distance_msg(self):
        self.outputLock.acquire()
        length = len(self.guidewireMovingDistance)
        ret = self.guidewireMovingDistance.pop(length-1)
        self.outputLock.release()
        return ret

    def get_latest_guidewire_moving_distance_sequence_length(self):
	self.outputLock.acquire()
        length = len(self.guidewireMovingDistance)
        self.outputLock.release()
        return length   
 
    def append_new_catheter_move_message(self, msg):
        self.inputLock.acquire()     
        self.catheterMoveInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_catheter_move_msg(self):
        self.inputLock.acquire()
        length = len(self.catheterMoveInstructionSequence)
        ret = self.catheterMoveInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_catheter_move_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.catheterMoveInstructionSequence)
        self.inputLock.release()
        return length

    def append_new_guidewire_progress_move_message(self, msg):
        self.inputLock.acquire()
        self.guidewireProgressInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_guidewire_progress_move_msg(self):
        self.inputLock.acquire()
        length = len(self.guidewireProgressInstructionSequence)
        ret = self.guidewireProgressInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_guidewire_progress_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.guidewireProgressInstructionSequence)
        self.inputLock.release()
        return length

    def append_new_guidewire_rotate_move_message(self, msg):
        self.inputLock.acquire()
        self.guidewireRotateInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_guidewire_rotate_move_msg(self):
        self.inputLock.acquire()
        length = len(self.guidewireRotateInstructionSequence)
        ret = self.guidewireRotateInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_guidewire_rotate_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.guidewireRotateInstructionSequence)
        self.inputLock.release()
        return length

    def append_new_contrast_media_push_move_message(self, msg):
        self.inputLock.acquire()
        self.contrastMediaPushInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_contrast_media_push_move_msg(self):
        self.inputLock.acquire()
        length = len(self.contrastMediaPushInstructionSequence)
        ret = self.contrastMediaPushInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_contrast_media_push_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.contrastMediaPushInstructionSequence)
        self.inputLock.release()
        return length

    def append_latest_retract_message(self, msg):
        self.inputLock.acquire()
        self.retractInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_retract_msg(self):
        self.inputLock.acquire()
        length = len(self.retractInstructionSequence)
        ret = self.retractInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_retract_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.retractInstructionSequence)
        self.inputLock.release()
        return length
