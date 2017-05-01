from pox.lib.addresses import IPAddr, EthAddr


class Eval:

    def __init__(self, decode):

        self._src_ip = None
        self._src_port = None
        self._dst_port = None
        self._protocol = None

        self.method = decode.get_method()
        self.args = decode.get_method_args()
        self.params = decode.get_params()

        self._eval()

    def _eval(self):
        if self.method == "DISCARD":
            self._src_ip = self.args[0]

            if "Source-Port" in self.params:
                self._src_port = int(self.params["Source-Port"])

            if "Destination-Port" in self.params:
                self._dst_port = int(self.params["Destination-Port"])

            if "Protocol" in self.params:
                self._protocol = self.params["Protocol"]

    @property
    def src_ip(self):
        return IPAddr(self._src_ip)

    @property
    def src_port(self):
        return self._src_port

    @property
    def dst_port(self):
        return self._dst_port

    @property
    def protocol(self):
        return self._protocol
