from RCPCom.TcpServer import TcpServer
from RCPCom.RCPClient import RCPClient
from RCPCom.RCPInputQueueManager import InputQueueManager
from RCPCom.RCPOutputQueueManager import OutputQueueManager
from RCPCom.RCPDatagramAnalyser import RCPDatagramAnalyser
from RCPCom.RCPDecodingTask import RCPDecodingTask
from RCPCom.RCPEncodingTask import RCPEncodingTask


class RCPComStack():
    def __init__(self, context):
        self.context = context
        self.inputQueueManager = InputQueueManager()
        self.outputQueueManager = OutputQueueManager()
        self.datagramAnalyser = RCPDatagramAnalyser(self, self.context)
        
        self.serv = TcpServer(self.inputQueueManager, 10704)
        self.serv.create_server()

        self.decodingTask = RCPDecodingTask(self.inputQueueManager, self.context, self.datagramAnalyser)
        self.encodingTask = RCPEncodingTask(self.context, self.outputQueueManager)

        self.clientList = list()

    def connectera(self, ip, port):
        client = RCPClient(self.outputQueueManager)
        client.connectera(ip, port)
        self.clientList.append(client)

    def launch_transmission_task_by_addr(self, addr):
        for client in self.clientList:
            if client.get_addr() == addr:
                client.launch()
