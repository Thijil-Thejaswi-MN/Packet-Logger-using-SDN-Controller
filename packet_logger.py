from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, icmp, arp
import datetime
import os

LOG_FILE = "packet_log.txt"

class PacketLogger(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PacketLogger, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        # Clear log file on start
        with open(LOG_FILE, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("       SDN PACKET LOGGER - SESSION STARTED\n")
            f.write(f"       {datetime.datetime.now()}\n")
            f.write("=" * 70 + "\n\n")
        self.logger.info("Packet Logger Controller Started. Logging to %s", LOG_FILE)

    def log_packet(self, msg):
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)
        icmp_pkt = pkt.get_protocol(icmp.icmp)
        arp_pkt = pkt.get_protocol(arp.arp)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}]\n")
            f.write(f"  ETH  | Src MAC: {eth.src}  ->  Dst MAC: {eth.dst}\n")

            if arp_pkt:
                f.write(f"  ARP  | Src IP: {arp_pkt.src_ip}  ->  Dst IP: {arp_pkt.dst_ip}\n")
                f.write(f"       | Protocol: ARP\n")
                self.logger.info("[ARP]  %s -> %s", arp_pkt.src_ip, arp_pkt.dst_ip)

            elif ip_pkt:
                f.write(f"  IP   | Src IP: {ip_pkt.src}  ->  Dst IP: {ip_pkt.dst}\n")

                if icmp_pkt:
                    f.write(f"       | Protocol: ICMP | Type: {icmp_pkt.type} | Code: {icmp_pkt.code}\n")
                    self.logger.info("[ICMP] %s -> %s", ip_pkt.src, ip_pkt.dst)

                elif tcp_pkt:
                    f.write(f"       | Protocol: TCP  | Src Port: {tcp_pkt.src_port}  ->  Dst Port: {tcp_pkt.dst_port}\n")
                    self.logger.info("[TCP]  %s:%s -> %s:%s", ip_pkt.src, tcp_pkt.src_port, ip_pkt.dst, tcp_pkt.dst_port)

                elif udp_pkt:
                    f.write(f"       | Protocol: UDP  | Src Port: {udp_pkt.src_port}  ->  Dst Port: {udp_pkt.dst_port}\n")
                    self.logger.info("[UDP]  %s:%s -> %s:%s", ip_pkt.src, udp_pkt.src_port, ip_pkt.dst, udp_pkt.dst_port)

                else:
                    f.write(f"       | Protocol: IP (other) | Proto#: {ip_pkt.proto}\n")

            f.write("-" * 70 + "\n")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # Default rule: send all unmatched packets to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("Switch connected: DPID %s", datapath.id)

    def add_flow(self, datapath, priority, match, actions, idle=0, hard=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                idle_timeout=idle, hard_timeout=hard,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        # Log the packet
        self.log_packet(msg)

        # Learning switch logic
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][eth.src] = in_port

        if eth.dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][eth.dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install flow rule so future packets don't hit controller
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst)
            self.add_flow(datapath, 1, match, actions, idle=10, hard=30)

        # Send packet out
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=ofproto.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=msg.data)
        datapath.send_msg(out)
