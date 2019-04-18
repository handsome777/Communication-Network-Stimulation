####################################################
# LSrouter.py
# Names:
# NetIds:
#####################################################

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads
from LSP import LSP
from Queue import PriorityQueue

COST_MAX = 16
class LSrouter(Router):
    """Link state routing protocol implementation."""

    def __init__(self, addr, heartbeatTime):
        """class fields and initialization code here"""
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.routersLSP = {}  ### 
        self.routersAddr = {} ###
        self.routersPort = {} ### 
        self.routersNext = {} ### 
        self.routersCost = {} ### 
        self.seqnum = 0 ###  
        self.routersLSP[self.addr] = LSP(self.addr, 0, {}) 

        self.lasttime = None
        self.heartbeat = heartbeatTime

    def handlePacket(self, port, packet):
        """process incoming packet"""
        # deal with traceroute packet
        #print "aaa"
        if packet.isTraceroute():
            if packet.dstAddr in self.routersNext:
                #print "aaaaaaaaaaa"
                next_nb = self.routersNext[packet.dstAddr]
                #print "src",packet.srcAddr,"next_nb",next_nb,"routersport",self.routersPort
                self.send(self.routersPort[next_nb], packet)
        # deal with routing packet
        transfer = False
        if packet.isRouting():
            if packet.dstAddr == packet.srcAddr:
                return

            packetIn = loads(packet.content)
            addr = packetIn["addr"]
            seqnum = packetIn["seqnum"]
            nbcost = packetIn["nbcost"]

            if addr not in self.routersLSP:
                self.routersLSP[addr] = LSP(addr, seqnum, nbcost)
                transfer = True
            if self.routersLSP[addr].updateLSP(packetIn):
                transfer = True

            if transfer:
                for portNext in self.routersAddr:
                    if portNext != port:
                        packet.srcAddr = self.addr
                        packet.dstAddr = self.routersAddr[portNext]
                        self.send(portNext, packet)


    def handleNewLink(self, port, endpoint, cost):
        """handle new link"""
        self.routersAddr[port] = endpoint
        self.routersPort[endpoint] = port
        self.routersLSP[self.addr].nbcost[endpoint] = cost

        content = {}   
        content["addr"] = self.addr
        content["seqnum"] = self.seqnum   
        content["nbcost"] = self.routersLSP[self.addr].nbcost
        self.seqnum += 1 # update the sequence number
        for port in self.routersAddr:
            packet = Packet(Packet.ROUTING, self.addr, self.routersAddr[port], dumps(content))
            self.send(port, packet)

    
    def calPath(self):
        # Dijkstra Algorithm for LS routing
        #print "begin calPath"
        #print self.routersLSP
        self.setCostMax()
        # put LSP info into a queue for operations
        Q = PriorityQueue()
        #print "sad",type(self.addr)
        for addr, nbcost in self.routersLSP[self.addr].nbcost.items():
            Q.put(node(addr, nbcost, addr))  
            #print addr, nbcost, addr
        while not Q.empty():
            con = 0

            n = Q.get(False)
            addr = n.p_addr
            cost = n.cost
            Next = n.addr

            
            if Next in self.routersCost:
                if addr not in self.routersCost:
                    self.routersNext[addr] = Next
                    self.routersCost[addr] = cost
                    con = 1
                else:
                    if cost < self.routersCost[addr]:
                        self.routersNext[addr] = Next
                        self.routersCost[addr] = cost
                        con = 1
            elif Next == addr:
                self.routersNext[addr] = Next
                self.routersCost[addr] = cost
                con = 1
                        

            #print "addr",type(addr)
            if (addr in self.routersLSP) and con:
                for addr1, nbcost1 in self.routersLSP[addr].nbcost.items():
                        Q.put(node(addr1, (nbcost1 + cost), Next))

        #print "over"

    def setCostMax(self):
        # intializtion for routing table 
        for addr in self.routersCost:
            self.routersCost[addr] = COST_MAX
        self.routersCost[self.addr] = 0
        self.routersNext[self.addr] = self.addr


    def handleRemoveLink(self, port):
        """handle removed link"""
        addr = self.routersAddr[port]
        self.routersLSP[self.addr].nbcost[addr] = COST_MAX
        self.calPath()

        content = {}
        content["addr"] = self.addr
        content["seqnum"] = self.seqnum + 1 
        content["nbcost"] = self.routersLSP[self.addr].nbcost
        self.seqnum += 1
        for port1 in self.routersAddr:
            if port1 != port:
                packet = Packet(Packet.ROUTING, self.addr, self.routersAddr[port1], dumps(content))
                self.send(port1, packet)
        pass

    def handleTime(self, timeMillisecs):
        """handle current time"""
        if (self.lasttime == None) or (timeMillisecs - self.lasttime > self.heartbeat):
            self.lasttime = timeMillisecs
            self.calPath()
      

    def debugString(self):
        out = str(self.routersNext) + "\n" + str(self.routersCost)
        print self.routersCost
        return out
        
class node():
    def __init__(self, p_addr, cost, addr):
        self.p_addr = p_addr
        self.cost = cost
        self.addr = addr
    def __lt__(self, other):
        return self.cost < other.cost