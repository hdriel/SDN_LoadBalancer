from pox.core import core
from pox.openflow import *
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.packet.arp import arp
from pox.lib.packet.ipv4 import ipv4
import time
import random
import json
from pprint import pprint
matplotlib_installed = True
try:
  import numpy as np
  import matplotlib.pyplot as plt
except: 
  matplotlib_installed = false

nameFile = "result_services.txt"
def printResultInPlot(data):
  try:
    services = []
    if (data is None): 
      with open(nameFile) as f: 
        for line in f:
          splitted = line.split(" ")
          val = splitted[len(splitted)-1]
        
          if val.endswith("\n"): val = val[0:len(val)-1]
          val = float(val)
          services.append(val)
    else: 
      services = data

    ind = np.arange(len(services))
    width = 0.35
    plt.bar(ind, services, width)
    plt.ylabel('Requests')
    plt.title('The amount of requests that handel each service of Load Balancer')
    plt.xticks(ind, ('S1', 'S2', 'S3', 'S4'))
    plt.show()
  except:
    print("You should to press Ctrl-C befor you type exit in mininet")

#############################################################################
c1_mac = "00:00:00:00:00:01"
c2_mac = "00:00:00:00:00:02"
c3_mac = "00:00:00:00:00:03"
c4_mac = "00:00:00:00:00:04"
s1_mac = "00:00:00:00:00:05"
s2_mac = "00:00:00:00:00:06"
s3_mac = "00:00:00:00:00:07"
s4_mac = "00:00:00:00:00:08"
srv_mac= "00:00:00:00:00:f1"
c1_ip  = "10.0.0.1"
c2_ip  = "10.0.0.2"
c3_ip  = "10.0.0.3"
c4_ip  = "10.0.0.4"
s1_ip  = "10.0.0.5"
s2_ip  = "10.0.0.6"
s3_ip  = "10.0.0.7"
s4_ip  = "10.0.0.8"
srv_ip = "10.1.2.3"

macToIp = { 
  c1_mac : c1_ip,
  c2_mac : c2_ip,
  c3_mac : c3_ip,
  c4_mac : c4_ip,
  s1_mac : s1_ip,
  s2_mac : s2_ip,
  s3_mac : s3_ip,
  s4_mac : s4_ip,
  srv_mac: srv_ip,
}

ipToMac = { 
  c1_ip : c1_mac,
  c2_ip : c2_mac,
  c3_ip : c3_mac,
  c4_ip : c4_mac,
  s1_ip : s1_mac,
  s2_ip : s2_mac,
  s3_ip : s3_mac,
  s4_ip : s4_mac,
  srv_ip: srv_mac,
}

macToPort = {
  c1_mac : 1,
  c2_mac : 2,
  c3_mac : 3,
  c4_mac : 4,
  s1_mac : 5,
  s2_mac : 6,
  s3_mac : 7,
  s4_mac : 8,
}

connectionUpDirection = {
  (srv_mac, c1_mac) : 1,
  (srv_mac, c2_mac) : 2,
  (srv_mac, c3_mac) : 3,
  (srv_mac, c4_mac) : 4,
  (srv_mac, s1_mac) : 5,
  (srv_mac, s2_mac) : 6,
  (srv_mac, s3_mac) : 7,
  (srv_mac, s4_mac) : 8
}

nameMac = {
  s1_mac : "s1",
  s2_mac : "s2",
  s3_mac : "s3",
  s4_mac : "s4",
  c1_mac : "c1",
  c2_mac : "c2",
  c3_mac : "c3",
  c4_mac : "c4",
  srv_mac: "mainServer"  
}

mappingRoutingPackets = {}
hosts_clients_mac     = [c1_mac, c2_mac, c3_mac, c4_mac]
hosts_servers_mac     = [s1_mac, s2_mac, s3_mac, s4_mac]
ip_services           = [s1_ip,s2_ip,s3_ip,s4_ip]
counter_servers       = {s1_mac: 0, s2_mac: 0, s3_mac:0 , s4_mac:0}

def initDictIpHost(clients = [c1_ip,c2_ip,c3_ip,c4_ip], services =[s1_ip,s2_ip,s3_ip,s4_ip], server = srv_ip):
  c1_ip =  clients[0]
  c2_ip =  clients[1]
  c3_ip =  clients[2]
  c4_ip =  clients[3]
  s1_ip = services[0]
  s2_ip = services[1]
  s3_ip = services[2]
  s4_ip = services[3]
  srv_ip = server
  ip_services = services

  ipToMac = { 
    c1_ip : c1_mac,
    c2_ip : c2_mac,
    c3_ip : c3_mac,
    c4_ip : c4_mac,
    s1_ip : s1_mac,
    s2_ip : s2_mac,
    s3_ip : s3_mac,
    s4_ip : s4_mac,
    srv_ip: srv_mac,
  }

##########################################
## Topology Assigment 2                 ##
##                                      ##
## +----+   +----+    +----+    +----+  ##
## | c1 |   | c2 |    | c3 |    | c4 |  ##
## +----+   +----+    +----+    +----+  ##
##       \1    |2       3|    4/        ##
##        +-------------------+         ##
##        |     server ip     |         ##
##        +-------------------+         ##
##       /5    |6       7|    8\        ##
## +----+   +----+    +----+    +----+  ##
## | s1 |   | s2 |    | s3 |    | s4 |  ##
## +----+   +----+    +----+    +----+  ##
##########################################

#############################################################################

def switch_routing(event):
  """ for now it like hub send packet to all links"""
  packet = event.parsed
  mac_src = str(packet.src)
  mac_dst = str(packet.dst)
  ip_src = str(packet.next.srcip)
  ip_dst = str(packet.next.dstip)
 

  flag_clinetSendToClient = (mac_dst in hosts_clients_mac and mac_src in hosts_clients_mac)
  flag_clinetSendToServer = (ip_dst == srv_ip)
  flag_serverSendToClient = (mac_dst in hosts_clients_mac)

  print "str(packet.next.srcip) : " , ip_src
  print "str(packet.src)        : " , mac_src
  print "str(packet.next.dstip) : " , ip_dst
  print "str(packet.dst)        : " , mac_dst
  print "flag_clinetSendToServer: " , flag_clinetSendToServer
  print "flag_serverSendToClient: " , flag_serverSendToClient

  if flag_clinetSendToClient:
    print "send packet from 'CLIENT' to 'CLIENT' ."
    _client_mac1 = mac_src
    _client_ip1  = ip_src
    _client_mac2 = mac_dst
    _client_ip2  = ip_dst
    outport     = macToPort[_client_mac2]
    
    addRuleClientClient(event, _client_ip1, _client_ip2, outport)
    e      = ethernet()
    e.type = ethernet.IP_TYPE
    e.src  = _client_mac1
    e.dst  = _client_ip2
    e.set_payload(packet.next)
    msg=of.ofp_packet_out()
    msg.data      = e.pack()
    msg.in_port   = event.port
    msg.actions.append(of.ofp_action_dl_addr.set_src(_client_mac1)    )
    msg.actions.append(of.ofp_action_dl_addr.set_dst(_client_mac2))
    msg.actions.append(of.ofp_action_nw_addr.set_src(IPAddr(_client_ip1)))
    msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr(_client_ip2)))
    msg.actions.append(of.ofp_action_output(port=outport)        )	
    event.connection.send(msg)
  elif flag_clinetSendToServer:
    print "send packet from 'CLIENT' to 'SERVER' ."
    _client_mac = mac_src
    _client_ip  = ip_src
    _LB_server = mac_dst

    # check if the client have not direction service yet
    if _client_mac in hosts_clients_mac:
      if _client_mac not in mappingRoutingPackets.keys():	
	random_server = random.choice(hosts_servers_mac)
	mappingRoutingPackets[_client_mac] = random_server
        print 'Add new mapping: ' , json.dumps(mappingRoutingPackets, indent = 1)
        counter_servers[random_server] = counter_servers[random_server] + 1
	print("Server selected %s " % random_server)

    outport     = macToPort[mappingRoutingPackets[_client_mac]]    
    _server_mac = mappingRoutingPackets[_client_mac]
    _server_ip  = macToIp[_server_mac] 
    addRuleClientServer(event, _client_ip, _server_ip, outport)
    e      = ethernet()
    e.type = ethernet.IP_TYPE
    e.src  = _LB_server
    e.dst  = _server_mac
    e.set_payload(packet.next)

    msg=of.ofp_packet_out()
    msg.data      = e.pack()
    msg.in_port   = event.port
			
    msg.actions.append(of.ofp_action_dl_addr.set_src(srv_mac)    ) 	
    msg.actions.append(of.ofp_action_dl_addr.set_dst(_server_mac)) 
    msg.actions.append(of.ofp_action_nw_addr.set_src(IPAddr(_client_ip)))	
    msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr(_server_ip))) 	
    msg.actions.append(of.ofp_action_output(port = outport)      )	
    event.connection.send(msg)
    del mappingRoutingPackets[_client_mac]
  elif flag_serverSendToClient:
    print "........"
    if mac_src in macToPort.keys():
      print "send packet from 'SERVER' to 'CLIENT' ."
      _server_ip  = str(packet.next.srcip)
      _server_mac = ipToMac[_server_ip] 
      
      key_from_value = None
      for key_mac in mappingRoutingPackets.keys():
        if mappingRoutingPackets[key_mac] == _server_mac: 
          key_from_value = key_mac
          break
      if key_from_value is None:
        return
      _client_mac = mappingRoutingPackets[key_from_value]
      print 'before remove [',_client_mac,'] : ' , json.dumps(mappingRoutingPackets, indent = 1)
      del mappingRoutingPackets[_client_mac]
      print 'AFTER remove [',_client_mac,'] : ' , json.dumps(mappingRoutingPackets, indent = 1)
      
      _client_ip  = macToIp[_client_mac]
      outport     = macToPort[_client_mac]
      addRuleServerClient(event, _server_ip, _client_ip, outport)
      e      = ethernet()
      e.type = ethernet.IP_TYPE
      e.src  = srv_mac
      e.dst  = _server_ip
      e.set_payload(packet.next)
      msg=of.ofp_packet_out()
      msg.data      = e.pack()
      msg.in_port   = event.port
      msg.actions.append(of.ofp_action_dl_addr.set_src(srv_mac)    )
      msg.actions.append(of.ofp_action_dl_addr.set_dst(_client_mac))
      msg.actions.append(of.ofp_action_nw_addr.set_src(IPAddr(_server_ip)))
      msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr(_client_ip)))
      msg.actions.append(of.ofp_action_output(port=outport)        )	
      evnet.connection.send(msg)

def addRuleClientClient(event, client_ip1, client_ip2, outport):
  print "addRuleClientClient: " ,client_ip1,"(",nameMac[ipToMac[client_ip1]],")" ," -> ", client_ip2 , "(",nameMac[ipToMac[client_ip2]],")" , "[ port = ",outport , "]"
  msg               = of.ofp_flow_mod()
  msg.command       = of.OFPFC_ADD	
  msg.match.dl_type = ethernet.IP_TYPE 	
  msg.match.nw_src  = IPAddr(client_ip1)
  msg.match.nw_dst  = IPAddr(client_ip2)
  msg.idle_timeout  = 10 			
  msg.buffer_id     = of.NO_BUFFER		
  msg.actions.append(of.ofp_action_dl_addr.set_src(ipToMac[client_ip1])) 
  msg.actions.append(of.ofp_action_dl_addr.set_dst(ipToMac[client_ip2]))
  msg.actions.append(of.ofp_action_nw_addr.set_src(IPAddr(client_ip1))) 
  msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr(client_ip2))) 	   
  msg.actions.append(of.ofp_action_output(port=outport)               )	
  event.connection.send(msg)

def addRuleServerClient(event, server_ip, client_ip, outport):
  print "addRuleServerClient: " ,server_ip,"(",nameMac[ipToMac[server_ip]],")" ," -> ", client_ip , "(",nameMac[ipToMac[client_ip]],")" , "[ port = ",outport , "]"
  msg               = of.ofp_flow_mod()
  msg.command       = of.OFPFC_ADD	
  msg.match.dl_type = ethernet.IP_TYPE 	
  msg.match.nw_src  = IPAddr(server_ip)
  msg.match.nw_dst  = IPAddr(client_ip)
  msg.idle_timeout  = 10 			
  msg.buffer_id     = of.NO_BUFFER		
  msg.actions.append(of.ofp_action_dl_addr.set_src(srv_mac)           ) 
  msg.actions.append(of.ofp_action_dl_addr.set_dst(ipToMac[client_ip]))
  msg.actions.append(of.ofp_action_nw_addr.set_src(srv_ip)            ) 
  msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr(client_ip))) 	   
  msg.actions.append(of.ofp_action_output(port=outport)               )	
  event.connection.send(msg)

def addRuleClientServer(event, client_ip, server_ip, outport):
  print "addRuleClientServer: " ,client_ip,"(",nameMac[ipToMac[client_ip]],")" ," -> ", server_ip , "(",nameMac[ipToMac[server_ip]],")" , "[ port = ",outport , "]"
  addRuleServerClient(event, server_ip, client_ip, event.port)
  msg               = of.ofp_flow_mod() 
  msg.command       = of.OFPFC_ADD 
  msg.match.dl_type = ethernet.IP_TYPE	
  msg.match.nw_src  = IPAddr(client_ip)
  msg.match.nw_dst  = IPAddr(srv_ip)
  msg.idle_timeout  = 10 	
  msg.buffer_id     = of.NO_BUFFER
  msg.actions.append(of.ofp_action_dl_addr.set_src(srv_mac)           )
  msg.actions.append(of.ofp_action_dl_addr.set_dst(ipToMac[server_ip]))
  msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr(server_ip))) 	
  msg.actions.append(of.ofp_action_output(port=outport)               ) 	
  event.connection.send(msg)

# handle ARP request and respond
def _arp(event):
  packet     = event.parsed
  arp_packet = packet.find('arp')  
  ip_src = str(arp_packet.protosrc)
  ip_dst = str(arp_packet.protodst)
  mac_src     = ipToMac[ip_src]
  mac_dst     = ipToMac[ip_dst]

  if arp_packet is not None:
    print "arp_packet.protosrc : " , ip_src , "(", nameMac[mac_src], ")"
    print "arp_packet.protodst : " , ip_dst , "(", nameMac[mac_dst], ")"

    if arp_packet.opcode == arp.REQUEST:      
      print "arp.REQUEST"
      #create arp packet
      a           = arp()
      a.opcode    = arp.REPLY

      #if request from src, fake reply from dst
      if arp_packet.hwsrc == EthAddr(mac_src): 
        a.hwsrc = EthAddr(mac_dst)
        a.hwdst = EthAddr(mac_src) 
      elif arp_packet.hwsrc == EthAddr(mac_dst):
        a.hwsrc = EthAddr(mac_src)
        a.hwdst = EthAddr(mac_dst)

      #fake reply IP
      a.protosrc  = IPAddr(ip_dst)
      a.protodst  = arp_packet.protosrc
      a.hwlen     = 6
      a.protolen  = 4
      a.hwtype    = arp.HW_TYPE_ETHERNET
      a.prototype = arp.PROTO_TYPE_IP
            
      #create ethernet packet
      e = ethernet()
      e.set_payload(a)
      e.type      = ethernet.ARP_TYPE
      if arp_packet.hwsrc == EthAddr(mac_src): 
        e.src = EthAddr(mac_dst)
        e.dst = EthAddr(mac_src) 
      elif arp_packet.hwsrc == EthAddr(mac_dst):
        e.src = EthAddr(mac_src)
        e.dst = EthAddr(mac_dst) 
    
      msg         = of.ofp_packet_out()
      msg.data    = e.pack()
      msg.actions.append(of.ofp_action_nw_addr(of.OFPAT_SET_NW_DST,IPAddr(ip_dst)))  
      msg.actions.append( of.ofp_action_output( port = event.port ) )
      event.connection.send(msg)

#############################################################################
def _handle_ConnectionUp (event):
  """ fire When the switches connect to the controller first time! """
  print "ConnectionUp event fired - init setup switch s", event.dpid, " !"
  ## create flow match rule   
  for k,port_out in connectionUpDirection.items(): 
    h1, h2 = k
    #for each packet from h1 to h2 in switch s forward via port p
    match = of.ofp_match()
    match.dl_src = EthAddr(h1)
    match.dl_dst = EthAddr(h2)
    msg = of.ofp_flow_mod()
    msg.match = match
    msg.hard_timeout = 300
    msg.idle_timeout = 100
    msg.actions.append(of.ofp_action_output(port=port_out))
    event.connection.send(msg)
  
def _handle_PacketIn(event):
  """fire each time host send a packet (ping) to another host... """
  packet = event.parsed
  if   packet.type == packet.ARP_TYPE:
    print("packet.ARP_TYPE")
    _arp(event)
    print "----------------------------------------------------\n"
  elif packet.type == packet.IP_TYPE:
    print("packet.IP_TYPE")
    switch_routing(event)
    print "----------------------------------------------------\n"
  

def _handle_ConnectionDown (event):
  """ fire When the switches connect to the controller first time! """
  print "ConnectionDown event fired - init setup switch s", event.dpid, " !"
  #print the plot histogram on handleing packet in each server...
  print "Amount Handleing services:" 
  print "s1: " , counter_servers[s1_mac]
  print "s2: " , counter_servers[s2_mac]
  print "s3: " , counter_servers[s3_mac]
  print "s4: " , counter_servers[s4_mac] , "\n"

  file = open(nameFile, "w")
  file.write('s1: {0}\n'.format(counter_servers[s1_mac]))
  file.write('s2: {0}\n'.format(counter_servers[s2_mac]))
  file.write('s3: {0}\n'.format(counter_servers[s3_mac]))
  file.write('s4: {0}'.format(counter_servers[s4_mac]))
  file.close()
  print('write the result to file \'{0}\''.format(nameFile))
  
  if (matplotlib_installed) : 
    services = [counter_servers[s1_mac], counter_servers[s2_mac], counter_servers[s3_mac], counter_servers[s4_mac]]
    printResultInPlot(services)

#############################################################################
def launch(ip = "", servers=""):
  if ip is not ""     : ip_server = str(ip)
  if servers is not "": ip_services = str(servers).split(',')
  initDictIpHost(services = ip_services, server = ip_server)
  
  print json.dumps(ipToMac, indent = 1)
  print "send to controller the following data:"
  print "ip\t", ip
  print "server\t", servers
  print "----------------------------------------------------\n"

  core.openflow.addListenerByName("ConnectionUp"  , _handle_ConnectionUp  )
  core.openflow.addListenerByName("PacketIn"      , _handle_PacketIn      )
  core.openflow.addListenerByName("ConnectionDown", _handle_ConnectionDown)
  print "Custom Controller running."
  



    
    
    


    
