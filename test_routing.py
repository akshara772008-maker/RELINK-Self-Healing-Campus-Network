from network.topology import CampusTopology
from network.routing import RoutingEngine


campus = CampusTopology()

graph = campus.get_graph()

router = RoutingEngine(graph)


source = "CSE-PC1"
destination = "LIB-PC1"


print("======================================")
print("DISTANCE VECTOR - NORMAL NETWORK")
print("======================================")


result = router.distance_vector_route(
    source,
    destination
)


print("Source:", source)
print("Destination:", destination)
print("Algorithm:", result["algorithm"])

if result["success"]:

    print("Path:", " → ".join(result["path"]))
    print("Cost:", result["cost"])

else:

    print("Route failed!")
    print(result["message"])


print("\n======================================")
print("FAILURE INJECTION")
print("======================================")


failed_router = "DIST-R1"

graph.nodes[failed_router]["status"] = "failed"

print("FAILED DEVICE:", failed_router)
print("Status: FAILED")


print("\n======================================")
print("DISTANCE VECTOR - AFTER FAILURE")
print("======================================")


result = router.distance_vector_route(
    source,
    destination
)


if result["success"]:

    print("New route found!")

    print("Path:", " → ".join(result["path"]))

    print("New cost:", result["cost"])

else:

    print("No alternate route available!")

    print(result["message"])