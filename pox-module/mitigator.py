from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, EthAddr
from protocol.proto_codec import Decode, Encode
from protocol.proto_eval import Eval

log = core.getLogger()


protocol_map = {
    "udp": 17,
    "tcp" : 6,
    "icmp": 1
}

glob_gateways = []
connections = []


def glob_gateways_obj():
    buffer = []
    for gw in glob_gateways:
        buffer.append(IPAddr(gw))
    return buffer


def _handle_PacketIn (event):
    packet = event.parsed

    if packet.find("udp"):
        if packet.find("ipv4").dstip in glob_gateways_obj():
            if packet.find("udp").dstport == 5653:
                log.info("UDP Packet to DstPort 5653 seen")
                udp_packet = packet.find("udp")
                payload = udp_packet.payload
                log.info("Payload: "+udp_packet.payload)

                dec = Decode(payload)
                eval = Eval(dec)

                mitigate_action(event,
                                packet.find("ipv4").srcip,
                                eval.src_ip,
                                protocol=eval.protocol,
                                src_port=eval.src_port,
                                dst_port=eval.dst_port
                                )


def mitigate_action(event, dst_ip, src_ip, **kwargs):
      log.info("Mitigation triggered")
      msg = of.ofp_flow_mod(idle_timeout=120, hard_timeout=240)
      msg.match.dl_type = 0x800 #IPv4
      msg.match.nw_src = src_ip
      msg.match.nw_dst = dst_ip

      if "protocol" in kwargs and kwargs["protocol"] is not None:
          msg.match.nw_proto = protocol_map[kwargs["protocol"]]
      if "dst_port" in kwargs and kwargs["dst_port"] is not None:
          msg.match.tp_dst = kwargs["dst_port"]
      if "src_port" in kwargs and kwargs["src_port"] is not None:
          msg.match.tp_dst = kwargs["src_port"]

      msg.actions.append(of.ofp_action_output(port=of.OFPP_NONE))
      # Propagate this rule across all OpenFlow devices known to the controller
      for conns in connections:
          conns.send(msg)
          log.info("Host " + str(src_ip) + " blocked for 120 sec (idle) 240 sec (hard) " + str(kwargs))



def _setUpListener(event):
  connections.append(event.connection)
  for gw in glob_gateways:
      msg = of.ofp_flow_mod()
      msg.match.dl_type = 0x800 #IPv4
      msg.match.nw_dst = IPAddr(gw)
      msg.match.nw_proto = 17 #UDP
      msg.match.tp_dst= 5653 #UDP Port 5653

      msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
      event.connection.send(msg)

      log.info("Installed Flow to redirect all traffic to "+gw+" Port 5653 to the controller")


def launch(gateways = "10.0.0.254"):
  """
  Starts the component
  """
  global glob_gateways
  glob_gateways = gateways.replace(",", " ").split()
  core.openflow.addListenerByName("ConnectionUp", _setUpListener)
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
