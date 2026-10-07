class PacketSimulator:

    def __init__(self, graph, routing_engine=None):
        self.graph = graph
        self.routing_engine = routing_engine
        self.packet_counter = 0

    def create_packet(
        self,
        source,
        destination,
        data,
        source_ip=None,
        destination_ip=None,
        protocol="TCP",
        source_port=None,
        destination_port=None
    ):
        self.packet_counter += 1

        packet = {
            "packet_id": self.packet_counter,
            "source": source,
            "destination": destination,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "protocol": protocol,
            "source_port": source_port,
            "destination_port": destination_port,
            "ttl": 64,
            "data": data,
            "status": "created",
            "current_node": source,
            "hop_count": 0,
            "path": [],
            "original_path": [],
            "route_history": [],
            "failed_nodes": [],
            "failed_links": [],
            "logs": [],
            "reroute_count": 0
        }

        if protocol == "TCP":
            packet["connection_state"] = "CLOSED"
            packet["logs"].append("TCP connection initialized")

        elif protocol == "UDP":
            packet["connection_state"] = "CONNECTIONLESS"
            packet["logs"].append(
                "UDP connectionless transmission selected"
            )

        return packet

    def establish_tcp_connection(self, packet):

        if packet["protocol"] != "TCP":
            return packet

        packet["logs"].append("TCP SYN sent")
        packet["logs"].append("TCP SYN-ACK received")
        packet["logs"].append("TCP ACK sent")
        packet["connection_state"] = "ESTABLISHED"
        packet["logs"].append("TCP connection established")

        return packet

    def start_transmission(self, packet, route):

        if not route:
            packet["status"] = "failed"
            packet["logs"].append("No route available")
            return packet

        if not packet["original_path"]:
            packet["original_path"] = route.copy()

        packet["route_history"].append({
            "type": "original",
            "path": route.copy()
        })

        if packet["protocol"] == "TCP":

            if packet.get("connection_state") != "ESTABLISHED":
                packet = self.establish_tcp_connection(packet)

        packet["path"] = route.copy()
        packet["status"] = "transmitting"
        packet["logs"].append("Packet transmission started")

        index = 0

        while index < len(route):

            node = route[index]

            if packet["ttl"] <= 0:

                packet["status"] = "failed"
                packet["logs"].append("Packet TTL expired")

                return packet

            if self.graph.nodes[node].get("status") != "active":

                packet["failed_nodes"].append(node)

                packet["logs"].append(
                    f"Failure detected at {node}"
                )

                if self.routing_engine is None:

                    packet["status"] = "blocked"
                    packet["current_node"] = node

                    packet["logs"].append(
                        f"Packet blocked at failed device: {node}"
                    )

                    return packet

                packet["reroute_count"] += 1

                packet["logs"].append(
                    "Self-healing activated"
                )

                new_route = self.routing_engine.link_state_route(
                    packet["current_node"],
                    packet["destination"]
                )

                if not new_route["success"]:

                    packet["status"] = "failed"

                    packet["logs"].append(
                        "Rerouting failed: No alternate route available"
                    )

                    return packet

                route = new_route["path"]

                packet["path"] = route.copy()

                packet["route_history"].append({
                    "type": "recovery",
                    "path": route.copy()
                })

                packet["logs"].append(
                    "Alternate route calculated"
                )

                packet["logs"].append(
                    "Recovery route: " + " → ".join(route)
                )

                index = 0

                continue

            packet["current_node"] = node
            packet["hop_count"] += 1
            packet["ttl"] -= 1

            packet["logs"].append(
                f"Packet reached {node}"
            )

            index += 1

        packet["status"] = "delivered"

        packet["logs"].append(
            "Packet delivered successfully"
        )

        if packet["protocol"] == "TCP":

            packet["connection_state"] = "CLOSED"

            packet["logs"].append(
                "TCP connection closed"
            )

        return packet