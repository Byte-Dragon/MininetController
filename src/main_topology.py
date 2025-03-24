#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork(cli=False):
    """
   	    def __init__( self, topo=None, switch=OVSKernelSwitch, host=Host,
                  controller=DefaultController, link=Link, intf=Intf,
                  build=True, xterms=False, cleanup=False, ipBase='10.0.0.0/8',
                  inNamespace=False,
                  autoSetMacs=False, autoStaticArp=False, autoPinCpus=False,
                  listenPort=None, waitConnected=False ):
           Create Mininet object.
           topo: Topo (topology) object or None
           switch: default Switch class
           host: default Host class/constructor
           controller: default Controller class/constructor
           link: default Link class/constructor
           intf: default Intf class/constructor
           ipBase: base IP address for hosts,
           build: build now from topo?
           xterms: if build now, spawn xterms?
           cleanup: if build now, cleanup before creating?
           inNamespace: spawn switches and controller in net namespaces?
           autoSetMacs: set MAC addrs automatically like IP addresses?
           autoStaticArp: set all-pairs static MAC addrs?
           autoPinCpus: pin hosts to (real) cores (requires CPULimitedHost)?
           listenPort: base listening port to open; will be incremented for
               each additional switch in the net if inNamespace=False 
        """    
    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/10')
    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController, ip='127.0.0.1', port=6633)
    '''c0 = net.addController(name='c0',
                           controller=OVSController,
                           protocol='tcp',
                           port=6633)'''
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1/24', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='10.0.0.7', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, ip='10.0.0.8', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(s1, s2, cls=TCLink, bw=10,delay=5)
    net.addLink(s2, s3, cls=TCLink, bw=10,delay=5)
    net.addLink(s3, s4, cls=TCLink, bw=10,delay=5)
    net.addLink(s1, h1, cls=TCLink, bw=10,delay=5)
    net.addLink(h2, s1, cls=TCLink, bw=10,delay=5)
    net.addLink(h3, s2, cls=TCLink, bw=10,delay=5)
    net.addLink(h4, s2, cls=TCLink, bw=10,delay=5)
    net.addLink(h5, s3, cls=TCLink, bw=10,delay=5)
    net.addLink(h6, s3, cls=TCLink, bw=10,delay=5)
    net.addLink(h7, s4, cls=TCLink, bw=10,delay=5)
    net.addLink(h8, s4, cls=TCLink, bw=10,delay=5)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('s4').start([c0])
    '''net.get('s1').cmd('sudo ovs-ofctl add-flow s1 actions=NORMAL')
    net.get('s2').cmd('sudo ovs-ofctl add-flow s2 actions=NORMAL')
    net.get('s3').cmd('sudo ovs-ofctl add-flow s3 actions=NORMAL')
    net.get('s4').cmd('sudo ovs-ofctl add-flow s4 actions=NORMAL')'''
 
    #info( '*** Post configure switches and hosts\n')
    if cli:
        CLI(net)
    return net
if __name__ == '__main__':
    setLogLevel('info')
    net = myNetwork(True)
