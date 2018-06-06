#!/usr/bin/python
 
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.topo import Topo


setLogLevel( 'info' )
info( '*** Init mininet Network\n' )
print '##########################################'
print '## Topology Assigment 2                 ##'
print '##                                      ##'
print '## +----+   +----+    +----+    +----+  ##'
print '## | c1 |   | c2 |    | c3 |    | c4 |  ##'
print '## +----+   +----+    +----+    +----+  ##'
print '##       \     |         |     /        ##'
print '##        +-------------------+         ##'
print '##        |     server ip     |         ##'
print '##        +-------------------+         ##'
print '##       /     |         |     \        ##'
print '## +----+   +----+    +----+    +----+  ##'
print '## | s1 |   | s2 |    | s3 |    | s4 |  ##'
print '## +----+   +----+    +----+    +----+  ##'
print '##########################################'

class AssingmentTopology(Topo):
   def __init__(self):
     Topo.__init__(self)
     
   def build(self):
     "Create a simulated network"
     #info( '*** Adding hosts\n' )
     c1 = self.addHost('c1', ip='10.0.0.1', mac='00:00:00:00:00:01')
     c2 = self.addHost('c2', ip='10.0.0.2', mac='00:00:00:00:00:02')
     c3 = self.addHost('c3', ip='10.0.0.3', mac='00:00:00:00:00:03')
     c4 = self.addHost('c4', ip='10.0.0.4', mac='00:00:00:00:00:04')
     s1 = self.addHost('s1', ip='10.0.0.5', mac='00:00:00:00:00:05')
     s2 = self.addHost('s2', ip='10.0.0.6', mac='00:00:00:00:00:06')
     s3 = self.addHost('s3', ip='10.0.0.7', mac='00:00:00:00:00:07')
     s4 = self.addHost('s4', ip='10.0.0.8', mac='00:00:00:00:00:08')

     #info( '*** Adding switches\n' )
     srv = self.addSwitch( 'sr', dpid='1' , mac='00:00:00:00:00:f1')
     
   
     #info( '*** Creating links\n' )
     self.addLink(c1, srv, port2=1)
     self.addLink(c2, srv, port2=2)
     self.addLink(c3, srv, port2=3)
     self.addLink(c4, srv, port2=4)
     self.addLink(s1, srv, port2=5)
     self.addLink(s2, srv, port2=6)
     self.addLink(s3, srv, port2=7)
     self.addLink(s4, srv, port2=8)


topo = AssingmentTopology()
net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1', protocol='tcp', port = 6633), link=TCLink)


info( '*** Starting network\n')
net.start()
info( '*** Running CLI\n' )
CLI( net )
info( '*** Stopping network' )
net.stop()

