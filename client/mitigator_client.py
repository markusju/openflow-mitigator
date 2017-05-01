from protocol.proto_codec import Encode
import argparse
import netifaces
import socket



parser = argparse.ArgumentParser(description="OpenFlow DDoS Mitigator Client")

parser.add_argument("src_ip",  help="IP from which the attack originates.", type=str)
parser.add_argument("--protocol", help="A Layer 3 protocol which matches the traffic aggregate to be blocked.", choices=["tcp", "udp", "icmp"])
parser.add_argument("--src_port", help="A source port which matches in the traffic aggregate to be blocked. (You must specify a protocol other than icmp)", type=int)
parser.add_argument("--dst_port", help="A destination port which matches in the traffic aggregate to be blocked. (You must specify a protocol other than icmp)", type=int)
args = parser.parse_args()


default_gw = netifaces.gateways()["default"][netifaces.AF_INET][0]


e = Encode()
e.method = "DISCARD"

e.method_args.append(args.src_ip)

if args.protocol is not None:
    e.params["Protocol"] = args.protocol

if args.src_port is not None:
    if args.protocol is None or args.protocol == "icmp":
        parser.error("You must specify a protocol other than icmp in order to use the --src_port parameter.")
    else:
        e.params["Source-Port"] = args.src_port

if args.dst_port is not None:
    if args.protocol is None or args.protocol == "icmp":
        parser.error("You must specify a protocol other than icmp in order to use the --dst_port parameter.")
    else:
        e.params["Destination-Port"] = args.dst_port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(str(e), (default_gw, 5653))

print "Request sent."

exit(0)




