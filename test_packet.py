from network.topology import CampusTopology
from network.routing import RoutingEngine
from network.packet_simulator import PacketSimulator
from network.ip_manager import IPAddressManager


campus = CampusTopology()

graph = campus.get_graph()

router = RoutingEngine(graph)

packet_simulator = PacketSimulator(graph)

ip_manager = IPAddressManager(graph)

ip_manager.assign_ip_addresses()


source = "CSE-PC1"
destination = "LIB-PC1"

source_ip = ip_manager.get_ip(source)
destination_ip = ip_manager.get_ip(destination)


print("======================================")
print("TCP / UDP PACKET SIMULATION")
print("======================================")


route_result = router.link_state_route(
    source,
    destination
)


if not route_result["success"]:

    print("No route available!")

else:

    packet = packet_simulator.create_packet(
        source,
        destination,
        "Hello from CSE",
        source_ip,
        destination_ip,
        "TCP",
        5000,
        80
    )

    packet = packet_simulator.start_transmission(
        packet,
        route_result["path"]
    )


    print("Packet ID:", packet["packet_id"])

    print("Source:", packet["source"])
    print("Source IP:", packet["source_ip"])
    print("Source Port:", packet["source_port"])

    print("Destination:", packet["destination"])
    print("Destination IP:", packet["destination_ip"])
    print("Destination Port:", packet["destination_port"])

    print("Protocol:", packet["protocol"])
    print("TTL:", packet["ttl"])

    print("Data:", packet["data"])

    print("Status:", packet["status"])

    print("Hop Count:", packet["hop_count"])


    print("\nPACKET PATH")
    print("--------------------------------------")

    print(
        " → ".join(packet["path"])
    )


    print("\nPACKET LOG")
    print("--------------------------------------")

    for log in packet["logs"]:

        print(log)