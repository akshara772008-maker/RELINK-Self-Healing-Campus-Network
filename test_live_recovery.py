from network.topology import CampusTopology
from network.routing import RoutingEngine
from network.failure_detector import FailureDetector
from network.self_healing import SelfHealingController
from network.packet_simulator import PacketSimulator


campus = CampusTopology()

graph = campus.get_graph()

routing_engine = RoutingEngine(graph)

failure_detector = FailureDetector(graph)

controller = SelfHealingController(
    graph,
    routing_engine,
    failure_detector
)

packet_simulator = PacketSimulator(graph)


source = "CSE-PC1"
destination = "LIB-PC1"


print("======================================")
print("LIVE PACKET SELF-HEALING")
print("======================================")


print("\nSTEP 1 - FIND INITIAL ROUTE")
print("--------------------------------------")


route_result = routing_engine.link_state_route(
    source,
    destination
)

initial_route = route_result["path"]

print(
    "Initial Route:",
    " → ".join(initial_route)
)

print(
    "Initial Cost:",
    route_result["cost"]
)


print("\nSTEP 2 - CREATE PACKET")
print("--------------------------------------")


packet = packet_simulator.create_packet(
    source,
    destination,
    "Emergency packet"
)

print(
    "Packet ID:",
    packet["packet_id"]
)


print("\nSTEP 3 - PACKET TRANSMISSION")
print("--------------------------------------")


packet["status"] = "transmitting"

new_route = initial_route


for index, node in enumerate(initial_route):

    print(
        "Packet at:",
        node
    )

    packet["current_node"] = node

    packet["hop_count"] = index


    if node == "SW-CSE":

        print("\n*** FAILURE OCCURS ***")

        failed_device = "DIST-R1"

        graph.nodes[failed_device]["status"] = "failed"

        print(
            "Failed Device:",
            failed_device
        )


        print("\n*** FAILURE DETECTION ***")


        failures = failure_detector.detect_failures()

        print(
            "Failed Devices:",
            failures["failed_devices"]
        )


        print("\n*** ROUTE RECALCULATION ***")


        recovery = controller.recover_route(
            source,
            destination
        )

        new_route = recovery["route"]["path"]

        print(
            "New Route:",
            " → ".join(new_route)
        )

        print(
            "New Cost:",
            recovery["route"]["cost"]
        )


        print("\n*** PACKET CONTINUES ***")

        break


print("\nSTEP 4 - CONTINUE PACKET")
print("--------------------------------------")


remaining_route = new_route


for index, node in enumerate(remaining_route):

    if node == source:

        continue

    packet["current_node"] = node

    packet["hop_count"] += 1

    print(
        "Packet reached:",
        node
    )


packet["status"] = "delivered"


print("\n======================================")
print("TRANSMISSION COMPLETE")
print("======================================")


print(
    "Packet ID:",
    packet["packet_id"]
)

print(
    "Final Status:",
    packet["status"]
)

print(
    "Final Destination:",
    packet["current_node"]
)

print(
    "Total Hops:",
    packet["hop_count"]
)