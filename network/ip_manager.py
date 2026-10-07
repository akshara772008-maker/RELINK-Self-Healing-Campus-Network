import ipaddress


class IPAddressManager:

    def __init__(self, graph):
        self.graph = graph

    def assign_ip_addresses(self):

        subnets = {
            "CSE": "192.168.10.0/24",
            "IT": "192.168.20.0/24",
            "AI": "192.168.30.0/24",
            "ECE": "192.168.40.0/24",
            "EEE": "192.168.50.0/24",
            "ADMIN": "192.168.60.0/24",
            "LIBRARY": "192.168.70.0/24",
            "LAB": "192.168.80.0/24"
        }

        for node, data in self.graph.nodes(data=True):

            if data.get("type") == "host":

                department = data.get("department")

                network = ipaddress.ip_network(
                    subnets[department]
                )

                hosts = list(network.hosts())

                self.graph.nodes[node]["ip_address"] = str(
                    hosts[9]
                )

                self.graph.nodes[node]["subnet"] = str(
                    network
                )

        router_ips = {
            "CORE-R1": "10.0.0.1",
            "CORE-R2": "10.0.0.2",
            "DIST-R1": "10.0.1.1",
            "DIST-R2": "10.0.2.1",
            "DIST-R3": "10.0.3.1",
            "DIST-R4": "10.0.4.1"
        }

        for router, ip_address in router_ips.items():

            self.graph.nodes[router]["ip_address"] = ip_address

            self.graph.nodes[router]["subnet"] = "10.0.0.0/16"

    def get_ip(self, device):

        if device not in self.graph:

            return None

        return self.graph.nodes[device].get(
            "ip_address"
        )

    def get_subnet(self, device):

        if device not in self.graph:

            return None

        return self.graph.nodes[device].get(
            "subnet"
        )