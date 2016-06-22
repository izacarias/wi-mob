from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import dpid as dpid_lib
from ryu.lib import stplib
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
# Used for Topology discover
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event, switches
import networkx as nx

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'stplib': stplib.Stp}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.stp = kwargs['stplib']
        self.net = nx.DiGraph()

        # Sample of stplib config.
        #  please refer to stplib.Stp.set_config() for details.
        stp_hello = 1
        stp_delay = 2
        config = {dpid_lib.str_to_dpid('0000000000000001'):
                    {'bridge': {'priority': 0x1000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000006'):
                    {'bridge': {'priority': 0x2000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000007'):
                    {'bridge': {'priority': 0x3000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000002'):
                    {'bridge': {'priority': 0x4000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000003'):
                    {'bridge': {'priority': 0x5000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000008'):
                    {'bridge': {'priority': 0x6000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000004'):
                    {'bridge': {'priority': 0x7000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000009'):
                    {'bridge': {'priority': 0x8000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000005'):
                    {'bridge': {'priority': 0x9000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000000010'):
                    {'bridge': {'priority': 0xa000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  # Need to configure the Station's STP priority
                  dpid_lib.str_to_dpid('0000000000001002'):
                    {'bridge': {'priority': 0xb000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000001003'):
                    {'bridge': {'priority': 0xc000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000001004'):
                    {'bridge': {'priority': 0xd000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000001005'):
                    {'bridge': {'priority': 0xe000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000001007'):
                    {'bridge': {'priority': 0xf000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000001008'):
                    {'bridge': {'priority': 0x10000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000001009'):
                    {'bridge': {'priority': 0x11000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}},
                  dpid_lib.str_to_dpid('0000000000001010'):
                    {'bridge': {'priority': 0x12000, 'fwd_delay': stp_delay,
                     'hello_time': stp_hello}}}
        self.stp.set_config(config)
        self.stp.set_config(config)

    def ls(self, obj):
        print("\n".join([x for x in dir(obj) if x[0] != "_"]))

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    def delete_flow(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        for dst in self.mac_to_port[datapath.id].keys():
            match = parser.OFPMatch(eth_dst=dst)
            mod = parser.OFPFlowMod(
                datapath, command=ofproto.OFPFC_DELETE,
                out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
                priority=1, match=match)
            datapath.send_msg(mod)

    @set_ev_cls(stplib.EventPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):

        # Discards truncated packets
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("Packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)

        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Ignoring lldp packet
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s",
                         dpid_lib.dpid_to_str(dpid), src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(stplib.EventTopologyChange, MAIN_DISPATCHER)
    def _topology_change_handler(self, ev):
        dp = ev.dp
        dpid_str = dpid_lib.dpid_to_str(dp.id)
        msg = 'Receive topology change event. Flush MAC table.'
        self.logger.debug("[dpid=%s] %s", dpid_str, msg)

        if dp.id in self.mac_to_port:
            self.delete_flow(dp)
            del self.mac_to_port[dp.id]

    @set_ev_cls(stplib.EventPortStateChange, MAIN_DISPATCHER)
    def _port_state_change_handler(self, ev):
        dpid_str = dpid_lib.dpid_to_str(ev.dp.id)
        of_state = {stplib.PORT_STATE_DISABLE: 'DISABLE',
                    stplib.PORT_STATE_BLOCK: 'BLOCK',
                    stplib.PORT_STATE_LISTEN: 'LISTEN',
                    stplib.PORT_STATE_LEARN: 'LEARN',
                    stplib.PORT_STATE_FORWARD: 'FORWARD'}
        self.logger.debug("[dpid=%s][port=%d] state=%s",
                          dpid_str, ev.port_no, of_state[ev.port_state])

    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        switch_list = get_switch(self, None)
        all_switches = [switch.dp.id for switch in switch_list]
        self.net.add_nodes_from(all_switches)

        links_list = get_link(self, None)
        # print links_list
        links = [(link.src.dpid, link.dst.dpid, {
                  'port': link.src.port_no}) for link in links_list]
        # print links
        self.net.add_edges_from(links)
        links = [(link.dst.dpid, link.src.dpid, {
                  'port': link.dst.port_no}) for link in links_list]
        # print links
        self.net.add_edges_from(links)
        print "**********List of links"
        print self.net.edges()
