from network.topology import CampusTopology
from network.routing import RoutingEngine


campus = CampusTopology()

graph = campus.get_graph()

router = RoutingEngine(graph)


source = "CSE-PC1"
destination = "LIB-PC1"


print("======================================")
print("NORMAL NETWORK")
print("======================================")


result = router.link_state_route(
    source,
    destination
)


print("Source:", source)
print("Destination:", destination)
print("Path:", " → ".join(result["path"]))
print("Cost:", result["cost"])


print("\n======================================")
print("LINK FAILURE")
print("======================================")


failed_source = "DIST-R1"
failed_destination = "DIST-R4"


graph[failed_source][failed_destination]["status"] = "failed"


print(
    "FAILED LINK:",
    failed_source,
    "<->",
    failed_destination
)

print("Status: FAILED")


print("\n======================================")
print("NETWORK AFTER LINK FAILURE")
print("======================================")


result = router.link_state_route(
    source,
    destination
)


if result["success"]:

    print("New route found!")

    print("New Path:", " → ".join(result["path"]))

    print("New Cost:", result["cost"])

else:

    print("No alternate route available!")

    print(result["message"])