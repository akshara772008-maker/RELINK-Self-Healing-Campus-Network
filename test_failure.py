from network.topology import CampusTopology
from network.routing import RoutingEngine

topology = CampusTopology()
graph = topology.get_graph()

router = RoutingEngine(graph)

source = "CSE-PC1"
destination = "LIB-PC1"

print("BEFORE FAILURE")
print("--------------------------------------")

route = router.link_state_route(source, destination)

print("Path:", " → ".join(route["path"]))
print("Cost:", route["cost"])

print()

print("FAILURE")
print("--------------------------------------")

graph.nodes["DIST-R4"]["status"] = "failed"

print("DIST-R4 has FAILED")

print()

print("AFTER FAILURE")
print("--------------------------------------")

route = router.link_state_route(source, destination)

if route["success"]:
    print("New Path:", " → ".join(route["path"]))
    print("New Cost:", route["cost"])
else:
    print("No route available")