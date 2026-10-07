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
print("SELF-HEALING CONTROLLER")
print("======================================")

print("\nNORMAL NETWORK")
print("--------------------------------------")

route = routing_engine.link_state_route(
    source,
    destination
)

print("Route:", " → ".join(route["path"]))
print("Cost:", route["cost"])

print("\nSIMULATING FAILURE")
print("--------------------------------------")

graph.nodes["DIST-R4"]["status"] = "failed"

print("DIST-R4 has FAILED")

print("\nSELF-HEALING")
print("--------------------------------------")

result = self_healing.recover(
    source,
    destination
)

print("Status:", result["status"])
print("Message:", result["message"])

print("\nFAILURE INFORMATION")
print("--------------------------------------")

failure = result["failure"]

print("Type:", failure["type"])

if failure["type"] == "network":

    print("Failed Nodes:", failure["nodes"])

    print("Failed Links:", failure["links"])

print("\nRECOVERY ROUTE")
print("--------------------------------------")

recovery = result["recovery"]

if recovery is not None and recovery["path"]:

    print(
        "New Route:",
        " → ".join(recovery["path"])
    )

    print("New Cost:", recovery["cost"])

    print(
        "Algorithm:",
        recovery["algorithm"]
    )

else:

    print("No alternate route available")