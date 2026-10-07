from network.topology import CampusTopology
from network.ip_manager import IPAddressManager


campus = CampusTopology()

graph = campus.get_graph()

ip_manager = IPAddressManager(graph)

ip_manager.assign_ip_addresses()


print("======================================")
print("IPv4 ADDRESSING")
print("======================================")


devices = [
    "CSE-PC1",
    "IT-PC1",
    "AI-PC1",
    "ECE-PC1",
    "EEE-PC1",
    "ADMIN-PC1",
    "LIB-PC1",
    "LAB-PC1",
    "CORE-R1",
    "CORE-R2",
    "DIST-R1",
    "DIST-R2",
    "DIST-R3",
    "DIST-R4"
]


for device in devices:

    print(
        device,
        "| IP:",
        ip_manager.get_ip(device),
        "| Subnet:",
        ip_manager.get_subnet(device)
    )