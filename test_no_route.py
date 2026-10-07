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
print("NO ALTERNATE ROUTE TEST")
print("======================================")

print("\nSTEP 1: NORMAL ROUTE")
print("--------------------------------------")

route = routing_engine.link_state_route(
    source,
    destination
)

print("Route:", " → ".join(route["path"]))
print("Cost:", route["cost"])

print("\nSTEP 2: SIMULATE CRITICAL FAILURE")
print("--------------------------------------")

graph.nodes["SW-CSE"]["status"] = "failed"

print("SW-CSE has FAILED")

print("\nSTEP 3: FAILURE DETECTION")
print("--------------------------------------")

failure = self_healing.detect_failure(
    source,
    destination
)

print("Status:", failure["status"])
print("Failed Nodes:", failure["nodes"])
print("Failed Links:", failure["links"])

print("\nSTEP 4: RECOVERY ATTEMPT")
print("--------------------------------------")

recovery = self_healing.calculate_recovery_route(
    source,
    destination
)

print("Status:", recovery["status"])

if recovery["path"]:

    print(
        "Recovery Route:",
        " → ".join(recovery["path"])
    )

    print("Recovery Cost:", recovery["cost"])

else:

    print("No alternate route available")

print("Message:", recovery["message"])

print("\n======================================")
print("NO ALTERNATE ROUTE TEST COMPLETED")
print("======================================")