from network.topology import CampusTopology
from network.routing import RoutingEngine
from network.failure_detector import FailureDetector
from network.self_healing import SelfHealingController

campus = CampusTopology()
graph = campus.get_graph()

routing_engine = RoutingEngine(graph)
failure_detector = FailureDetector(graph)

self_healing = SelfHealingController(
    graph,
    routing_engine,
    failure_detector
)

source = "CSE-PC1"
destination = "LIB-PC1"

print("======================================")
print("LINK FAILURE SELF-HEALING TEST")
print("======================================")

print("\nSTEP 1: NORMAL ROUTE")
print("--------------------------------------")

route = routing_engine.link_state_route(
    source,
    destination
)

print("Route:", " → ".join(route["path"]))
print("Cost:", route["cost"])

print("\nSTEP 2: SIMULATE LINK FAILURE")
print("--------------------------------------")

graph["DIST-R1"]["DIST-R4"]["status"] = "failed"

print("Link DIST-R1 <-> DIST-R4 has FAILED")

print("\nSTEP 3: FAILURE DETECTION")
print("--------------------------------------")

failure = self_healing.detect_failure(
    source,
    destination
)

print("Status:", failure["status"])
print("Failed Nodes:", failure["nodes"])
print("Failed Links:", failure["links"])

print("\nSTEP 4: RECOVERY ROUTE")
print("--------------------------------------")

recovery = self_healing.calculate_recovery_route(
    source,
    destination
)

print("Status:", recovery["status"])

if recovery["path"]:
    print(
        "New Route:",
        " → ".join(recovery["path"])
    )

    print("New Cost:", recovery["cost"])
    print("Algorithm:", recovery["algorithm"])

else:
    print("No alternate route available")

print("\n======================================")
print("LINK FAILURE TEST COMPLETED")
print("======================================")