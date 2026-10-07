from network.topology import CampusTopology
from network.routing import RoutingEngine
from network.packet_simulator import PacketSimulator

topology = CampusTopology()
graph = topology.get_graph()

routing_engine = RoutingEngine(graph)

packet_simulator = PacketSimulator(
    graph,
    routing_engine
)

source = "CSE-PC1"
destination = "LIB-PC1"

route = routing_engine.link_state_route(
    source,
    destination
)

packet = packet_simulator.create_packet(
    source=source,
    destination=destination,
    source_ip="192.168.10.10",
    destination_ip="192.168.70.10",
    source_port=5000,
    destination_port=80,
    protocol="TCP",
    data="Hello from CSE"
)

graph.nodes["DIST-R4"]["status"] = "failed"

result = packet_simulator.start_transmission(
    packet,
    route["path"]
)

print("======================================")
print("SELF-HEALING PACKET SIMULATION")
print("======================================")

print("Packet ID:", result["packet_id"])
print("Source:", result["source"])
print("Destination:", result["destination"])
print("Protocol:", result["protocol"])
print("Status:", result["status"])
print("Reroute Count:", result["reroute_count"])
print("Hop Count:", result["hop_count"])
print("TTL:", result["ttl"])

print()
print("FINAL PACKET PATH")
print("--------------------------------------")
print(" → ".join(result["path"]))

print()
print("PACKET LOG")
print("--------------------------------------")

for log in result["logs"]:
    print(log)