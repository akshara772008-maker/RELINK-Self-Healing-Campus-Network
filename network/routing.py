import networkx as nx


class RoutingEngine:

    def __init__(self, graph):
        self.graph = graph

    def link_state_route(self, source, destination):

        active_graph = self._get_active_graph()

        try:

            path = nx.dijkstra_path(
                active_graph,
                source,
                destination,
                weight="cost"
            )

            cost = nx.dijkstra_path_length(
                active_graph,
                source,
                destination,
                weight="cost"
            )

            return {
                "success": True,
                "algorithm": "Link State - Dijkstra",
                "source": source,
                "destination": destination,
                "path": path,
                "cost": cost
            }

        except nx.NetworkXNoPath:

            return {
                "success": False,
                "algorithm": "Link State - Dijkstra",
                "source": source,
                "destination": destination,
                "path": [],
                "cost": None,
                "message": "No route available"
            }

        except nx.NodeNotFound as error:

            return {
                "success": False,
                "algorithm": "Link State - Dijkstra",
                "source": source,
                "destination": destination,
                "path": [],
                "cost": None,
                "message": str(error)
            }

    def distance_vector_route(self, source, destination):

        active_graph = self._get_active_graph()

        if source not in active_graph:

            return {
                "success": False,
                "algorithm": "Distance Vector - Bellman-Ford",
                "source": source,
                "destination": destination,
                "path": [],
                "cost": None,
                "message": "Source device is unavailable"
            }

        if destination not in active_graph:

            return {
                "success": False,
                "algorithm": "Distance Vector - Bellman-Ford",
                "source": source,
                "destination": destination,
                "path": [],
                "cost": None,
                "message": "Destination device is unavailable"
            }

        nodes = list(active_graph.nodes())

        distance = {
            node: float("inf")
            for node in nodes
        }

        previous = {
            node: None
            for node in nodes
        }

        distance[source] = 0

        for _ in range(len(nodes) - 1):

            updated = False

            for current in nodes:

                if distance[current] == float("inf"):
                    continue

                for neighbour in active_graph.neighbors(current):

                    edge_data = active_graph[current][neighbour]

                    cost = edge_data.get("cost", 1)

                    new_distance = distance[current] + cost

                    if new_distance < distance[neighbour]:

                        distance[neighbour] = new_distance

                        previous[neighbour] = current

                        updated = True

            if not updated:
                break

        if distance[destination] == float("inf"):

            return {
                "success": False,
                "algorithm": "Distance Vector - Bellman-Ford",
                "source": source,
                "destination": destination,
                "path": [],
                "cost": None,
                "message": "No route available"
            }

        path = []

        current = destination

        while current is not None:

            path.append(current)

            current = previous[current]

        path.reverse()

        return {
            "success": True,
            "algorithm": "Distance Vector - Bellman-Ford",
            "source": source,
            "destination": destination,
            "path": path,
            "cost": distance[destination]
        }

    def _get_active_graph(self):

        active_graph = self.graph.copy()

        failed_nodes = [
            node
            for node, data in active_graph.nodes(data=True)
            if data.get("status") != "active"
        ]

        active_graph.remove_nodes_from(failed_nodes)

        failed_edges = [
            (source, destination)
            for source, destination, data in active_graph.edges(data=True)
            if data.get("status") != "active"
        ]

        active_graph.remove_edges_from(failed_edges)

        return active_graph