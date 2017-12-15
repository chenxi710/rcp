from RCPContext.RCPContext import RCPContext
import RCPDatagram
from MotorMsg import MotorMsg


class RCPDatagramAnalyser:
    def __init__(self, parent, context):
        self.parent = parent
        self.context = context
        self.switcher = {
            0: "HelloMsg",
            1: "HandShakeMsg",
            2: "HandShakeCommitMsg",
            3: "MotorMsg",
            4: "CTImage",
	    5: "CloseSessionMsg"
        }

        self.switcher_instruction = {
            0: "catheterMoveInstruction",
            1: "guidewireProgressInstruction",
            2: "guidewireRotateInstruction",
            3: "contrastMediaPushInstruction",
            4: "retractInstruction"
        }

    def analyse(self, cpt, datagram):
        if self.switcher[datagram.get_data_type()] == "HelloMsg":
            self.decode_hello_message(datagram)
        elif self.switcher[datagram.get_data_type()] == "HandShakeMsg":
            pass
        elif self.switcher[datagram.get_data_type()] == "HandShakeCommitMsg":
            self.decode_handshake_commit_message(datagram)
        elif self.switcher[datagram.get_data_type()] == "MotorMsg":
            self.decode_motor_message(datagram)
        elif self.switcher[datagram.get_data_type()] == "CTImage":
            pass
	elif self.switcher[datagram.get_data_type()] == "CloseSessionMsg":
	    self.decode_close_session_message(datagram)	
    
    def decode_close_session_message(self, datagram):
	datagram_body = datagram.get_itc_datagram_body()	
	self.parent.close_session()	

    def decode_hello_message(self, datagram):
	x = 1

    def decode_motor_message(self, datagram):
        
        motor_msg = MotorMsg(datagram)
        
        if self.switcher_instruction[motor_msg.motor_type] == "catheterMoveInstruction":
#            print "catheterMoveInstruction"
#            print "speed--------------------------", motor_msg.get_motor_speed()
            self.context.append_new_catheter_move_message(motor_msg)
        elif self.switcher_instruction[motor_msg.motor_type] == "guidewireProgressInstruction":
#            print "guidewireProgressInstruction"
            self.context.append_new_guidewire_progress_move_message(motor_msg)
        elif self.switcher_instruction[motor_msg.motor_type] == "guidewireRotateInstruction":
#            print "guidewireRotateInstruction"
            self.context.append_new_guidewire_rotate_move_message(motor_msg)
        elif self.switcher_instruction[motor_msg.motor_type] == "contrastMediaPushInstruction":
            self.context.append_new_contrast_media_push_move_message(motor_msg)
        elif self.switcher_instruction[motor_msg.motor_type] == "retractInstruction":
#            print "retractInstruction"
            self.context.append_latest_retract_message(motor_msg)

    def decode_handshake_commit_message(self, datagram):
        datagram_body = datagram.get_itc_datagram_body()
        addr = str(ord(datagram_body[0])) + '.' + str(ord(datagram_body[1])) + '.' + str(ord(datagram_body[2])) + '.' + str(ord(datagram_body[3]))
        self.parent.launch_transmission_task_by_addr(addr)
