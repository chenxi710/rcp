# -*- coding: utf-8 -*-
import io
import os
import socket
import struct
import mmap
import threading
import time
from RCPDatagram import RCPDatagram


class Client:
    def __init__(self, _soc, _addr, _num, _input_queue_manager):
        self.soc = _soc
        self.addr = _addr
        self.clientIndex = _num
        self.inputQueueManager = _input_queue_manager

        self.counter_save = 0
        self.counter_save_rec = 0
        self.counter_save_nor = 0
        self.serFileMsg = None
        self.systemStatus = 'standby'
        self.ready = False
        self.reconstruct_count = 0
        self.navi_count = 0
        self.pos_init = 10000000
        self.pos_count = 0
        self.fileSize = 1560 * 1440 * 2
        self.cpt = 0
        
        self.receptionTask = threading.Thread(None, self.reception)

    def recvall(self, sock, count):
        buf = b''
        while count:
            new_buf = sock.recv(count)
            if not new_buf:
                return None
            buf += new_buf
            count -= len(new_buf)
        return buf

    def set_current_state(self, current_state):
        self.systemStatus = current_state

    def enable(self):
        self.systemStatus = 'navi'
        self.receptionTask.start()

    def reception(self):
        while True:
            # send system status to incoming client
            msg = self.recvall(self.soc, 1024)
#            print 'msg arriving'
            datagram = RCPDatagram(msg)

#            print "get_data_type",self.clientIndex, datagram.get_data_type()

            self.inputQueueManager.add_datagram_by_id(self.clientIndex, datagram)
            self.cpt += 1
            time.sleep(0.02)

    def is_ready(self):
        return self.ready

    def get_id(self):
        return self.clientIndex

    def find_order(self, line):
        line_date = line.translate(None, "\r\n")
        p = line_date.find(':')
        data = line_date[p + 1:len(line_date)]
        return data

    def send_order(self, _order):
        # print len(_order), _order
        self.soc.sendall(str(len(_order)).ljust(16))
        self.soc.sendall(_order)
        # print "transmitted...."
