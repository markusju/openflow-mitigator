#!/usr/bin/python                                                                            

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import Controller, RemoteController
from mininet.node import OVSSwitch


class SdnProjectTopo(Topo):
    "Single switch connected to n hosts."
    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        h1 = self.addHost('h1', ip='10.0.0.1/24', defaultRoute='via 10.0.0.254')
        h2 = self.addHost('h2', ip='10.0.0.2/24', defaultRoute='via 10.0.0.254')
        h3 = self.addHost('h3', ip='11.0.0.3/24', defaultRoute='via 11.0.0.254')
        h4 = self.addHost('h4', ip='11.0.0.4/24', defaultRoute='via 11.0.0.254')


        self.addLink(h1, s1)
        self.addLink(h2, s1)
        
        self.addLink(h3, s2)
        self.addLink(h4, s2)


        self.addLink(s1, s2)

def simpleTest():
    "Create and test a simple network"
    topo = SingleSwitchTopo(n=4)
    net = Mininet(topo)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    topo = SdnProjectTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=Controller)
    net.start()

    # Transfernetz einrichten...
    net.get('s1').intf('s1-eth3').setIP('10.0.0.254/24')
    net.get('s2').intf('s2-eth3').setIP('11.0.0.254/24')   

    #net.get('s1').intf('s1-eth3').setMAC('62:a7:62:3f:47:cf')
    #net.get('s2').intf('s2-eth3').setMAC('66:20:67:0f:88:77') 



    CLI(net)
    net.stop()

topos = { 'sdnprojecttopo': lambda: SdnProjectTopo() }


