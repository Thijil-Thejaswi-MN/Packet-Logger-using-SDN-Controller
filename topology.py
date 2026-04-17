from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def create_topology():
    net = Mininet(controller=RemoteController, link=TCLink)

    print("[*] Adding controller...")
    c0 = net.addController('c0', controller=RemoteController,
                            ip='127.0.0.1', port=6633)

    print("[*] Adding switch...")
    s1 = net.addSwitch('s1')

    print("[*] Adding hosts...")
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')

    print("[*] Creating links...")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    print("[*] Starting network...")
    net.start()

    print("\n" + "="*50)
    print("  Network Topology Ready!")
    print("  Hosts: h1(10.0.0.1), h2(10.0.0.2), h3(10.0.0.3)")
    print("  Switch: s1  |  Controller: 127.0.0.1:6633")
    print("="*50 + "\n")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
