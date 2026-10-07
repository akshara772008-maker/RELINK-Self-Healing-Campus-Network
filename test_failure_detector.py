from network.topology import CampusTopology
from network.failure_detector import FailureDetector

campus = CampusTopology()

graph = campus.get_graph()

detector = FailureDetector(graph)

print("======================================")
print("FAILURE DETECTION MODULE")
print("======================================")

print("\nDEVICE CHECK")
print("--------------------------------------")

graph.nodes["DIST-R1"]["status"] = "failed"

result = detector.check_device("DIST-R1")

print("Device:", result["device"])
print("Status:", result["status"])
print("Reachable:", result["reachable"])
print("Message:", result["message"])

print("\nLINK CHECK")
print("--------------------------------------")

graph["DIST-R1"]["DIST-R4"]["status"] = "failed"

result = detector.check_link(
    "DIST-R1",
    "DIST-R4"
)

print(
    "Link:",
    result["source"],
    "<->",
    result["destination"]
)

print("Status:", result["status"])
print("Reachable:", result["reachable"])
print("Message:", result["message"])