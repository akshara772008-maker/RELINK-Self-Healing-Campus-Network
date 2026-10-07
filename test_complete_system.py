from network.topology import CampusTopology
from network.routing import RoutingEngine
from network.failure_detector import FailureDetector
from network.self_healing import SelfHealingController
from network.packet_simulator import PacketSimulator

campus = CampusTopology()
graph = campus.get_graph()

routing_engine = RoutingEngine(graph)
failure_detector = FailureDetector(graph)

self_healing = SelfHealingController(
    graph,
    routing_engine,
    failure_detector
)

packet_simulator = PacketSimulator(
    graph,
    routing_engine
)

source = "CSE-PC1"
destination = "LIB-PC1"

print("======================================")
print("COMPLETE SELF-HEALING NETWORK SYSTEM")
print("======================================")

print("\nSTEP 1: INITIAL ROUTE")
print("--------------------------------------")

route = routing_engine.link_state_route(
    source,
    destination
)

print("Source:", source)
print("Destination:", destination)
print("Route:", " → ".join(route["path"]))
print("Cost:", route["cost"])

print("\nSTEP 2: CREATE PACKET")
print("--------------------------------------")

packet = packet_simulator.create_packet(
    source=source,
    destination=destination,
    data="Emergency network message",
    source_ip="192.168.10.10",
    destination_ip="192.168.70.10",
    protocol="TCP",
    source_port=5000,
    destination_port=80
)

print("Packet ID:", packet["packet_id"])
print("Protocol:", packet["protocol"])
print("Data:", packet["data"])

print("\nSTEP 3: SIMULATE NETWORK FAILURE")
print("--------------------------------------")

graph.nodes["DIST-R4"]["status"] = "failed"

print("DIST-R4 has FAILED")

print("\nSTEP 4: FAILURE DETECTION")
print("--------------------------------------")

failure = self_healing.detect_failure(
    source,
    destination
)

print("Status:", failure["status"])
print("Failed Nodes:", failure["nodes"])
print("Failed Links:", failure["links"])

print("\nSTEP 5: CALCULATE RECOVERY ROUTE")
print("--------------------------------------")

recovery = self_healing.calculate_recovery_route(
    source,
    destination
)

print("Status:", recovery["status"])
print("New Route:", " → ".join(recovery["path"]))
print("New Cost:", recovery["cost"])
print("Algorithm:", recovery["algorithm"])

print("\nSTEP 6: PACKET SELF-HEALING")
print("--------------------------------------")

packet = packet_simulator.start_transmission(
    packet,
    route["path"]
)

print("Packet Status:", packet["status"])
print("Reroute Count:", packet["reroute_count"])
print("Hop Count:", packet["hop_count"])
print("Final Node:", packet["current_node"])

print("\nPACKET LOG")
print("--------------------------------------")

for log in packet["logs"]:
    print(log)
print("\nROUTE HISTORY")
print("--------------------------------------")

for route_info in packet["route_history"]:

    print(
        route_info["type"].upper() + " ROUTE:"
    )

    print(
        " → ".join(route_info["path"])
    )

print("\nFAILED DEVICES")
print("--------------------------------------")

if packet["failed_nodes"]:
    for node in packet["failed_nodes"]:
        print(node)
else:
    print("None")

print("\nFINAL PACKET INFORMATION")
print("--------------------------------------")

print("Original Route:")
print(" → ".join(packet["original_path"]))

print("Final Route:")
print(" → ".join(packet["path"]))

print("Reroute Count:", packet["reroute_count"])
print("Final Status:", packet["status"])
print("\n======================================")
print("SYSTEM TEST COMPLETED")
print("======================================")