from network.topology import CampusTopology


campus = CampusTopology()

graph = campus.get_graph()

print("======================================")
print("SELF-HEALING CAMPUS NETWORK")
print("======================================")

print("Total devices:", graph.number_of_nodes())
print("Total links:", graph.number_of_edges())

print("\nDEVICES")
print("--------------------------------------")

for node, data in graph.nodes(data=True):

    print(
        node,
        "| Type:",
        data["type"],
        "| Status:",
        data["status"]
    )

print("\nLINKS")
print("--------------------------------------")

for source, destination, data in graph.edges(data=True):

    print(
        source,
        "<->",
        destination,
        "| Cost:",
        data["cost"],
        "| Status:",
        data["status"]
    )