class FailureDetector:

    def __init__(self, graph):
        self.graph = graph

    def check_device(self, device):

        if device not in self.graph:

            return {
                "device": device,
                "reachable": False,
                "status": "UNKNOWN",
                "message": "Device does not exist"
            }

        status = self.graph.nodes[device].get(
            "status",
            "active"
        )

        if status == "active":

            return {
                "device": device,
                "reachable": True,
                "status": "ACTIVE",
                "message": "Device is reachable"
            }

        return {
            "device": device,
            "reachable": False,
            "status": "FAILED",
            "message": "Device is not reachable"
        }

    def check_link(self, source, destination):

        if not self.graph.has_edge(source, destination):

            return {
                "source": source,
                "destination": destination,
                "reachable": False,
                "status": "UNKNOWN",
                "message": "Link does not exist"
            }

        status = self.graph[source][destination].get(
            "status",
            "active"
        )

        if status == "active":

            return {
                "source": source,
                "destination": destination,
                "reachable": True,
                "status": "ACTIVE",
                "message": "Link is active"
            }

        return {
            "source": source,
            "destination": destination,
            "reachable": False,
            "status": "FAILED",
            "message": "Link has failed"
        }

    def check_all_devices(self):

        results = []

        for device in self.graph.nodes:

            results.append(
                self.check_device(device)
            )

        return results

    def check_all_links(self):

        results = []

        for source, destination in self.graph.edges:

            results.append(
                self.check_link(
                    source,
                    destination
                )
            )

        return results

    def detect_failures(self):

        failed_devices = []
        failed_links = []

        for device, data in self.graph.nodes(data=True):

            if data.get("status") != "active":

                failed_devices.append(device)

        for source, destination, data in self.graph.edges(data=True):

            if data.get("status") != "active":

                failed_links.append(
                    (source, destination)
                )

        return {
            "failed_devices": failed_devices,
            "failed_links": failed_links
        }