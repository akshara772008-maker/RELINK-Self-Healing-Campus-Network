class SelfHealingController:

    def __init__(self, graph, routing_engine, failure_detector):
        self.graph = graph
        self.routing_engine = routing_engine
        self.failure_detector = failure_detector
        self.recovery_log = []

    def detect_failure(self, source=None, destination=None):

        failed_nodes = []

        for node, data in self.graph.nodes(data=True):

            if data.get("status") != "active":
                failed_nodes.append(node)

        failed_links = []

        for source_node, destination_node, data in self.graph.edges(data=True):

            if data.get("status") != "active":
                failed_links.append(
                    (source_node, destination_node)
                )

        if failed_nodes or failed_links:

            failure = {
                "type": "network",
                "nodes": failed_nodes,
                "links": failed_links,
                "source": source,
                "destination": destination,
                "status": "failure_detected",
                "message": "Network failure detected"
            }

            self.recovery_log.append(failure)

            return failure

        return {
            "type": "network",
            "nodes": [],
            "links": [],
            "source": source,
            "destination": destination,
            "status": "normal",
            "message": "No failure detected"
        }

    def calculate_recovery_route(self, source, destination):

        route = self.routing_engine.link_state_route(
            source,
            destination
        )

        if route["success"]:

            recovery = {
                "status": "recovered",
                "source": source,
                "destination": destination,
                "path": route["path"],
                "cost": route["cost"],
                "algorithm": route["algorithm"],
                "message": "Alternate route calculated successfully"
            }

            self.recovery_log.append(recovery)

            return recovery

        recovery = {
            "status": "failed",
            "source": source,
            "destination": destination,
            "path": [],
            "cost": None,
            "algorithm": route["algorithm"],
            "message": "No alternate route available"
        }

        self.recovery_log.append(recovery)

        return recovery

    def recover(self, source, destination):

        failure = self.detect_failure(
            source,
            destination
        )

        if failure["status"] == "normal":

            return {
                "status": "normal",
                "failure": failure,
                "recovery": None,
                "message": "Network is operating normally"
            }

        recovery = self.calculate_recovery_route(
            source,
            destination
        )

        return {
            "status": recovery["status"],
            "failure": failure,
            "recovery": recovery,
            "message": recovery["message"]
        }

    def get_recovery_log(self):

        return self.recovery_log