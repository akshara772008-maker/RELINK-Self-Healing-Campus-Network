import networkx as nx


class CampusTopology:

    def __init__(self):
        self.graph = nx.Graph()
        self.build_topology()

    def build_topology(self):

        devices = {

            # Core Routers
            "CORE-R1": {
                "type": "router",
                "layer": "core"
            },

            "CORE-R2": {
                "type": "router",
                "layer": "core"
            },

            # Distribution Routers
            "DIST-R1": {
                "type": "router",
                "layer": "distribution"
            },

            "DIST-R2": {
                "type": "router",
                "layer": "distribution"
            },

            "DIST-R3": {
                "type": "router",
                "layer": "distribution"
            },

            "DIST-R4": {
                "type": "router",
                "layer": "distribution"
            },

            # Access Switches
            "SW-CSE": {
                "type": "switch",
                "layer": "access"
            },

            "SW-IT": {
                "type": "switch",
                "layer": "access"
            },

            "SW-AI": {
                "type": "switch",
                "layer": "access"
            },

            "SW-ECE": {
                "type": "switch",
                "layer": "access"
            },

            "SW-EEE": {
                "type": "switch",
                "layer": "access"
            },

            "SW-ADMIN": {
                "type": "switch",
                "layer": "access"
            },

            "SW-LIB": {
                "type": "switch",
                "layer": "access"
            },

            "SW-LAB": {
                "type": "switch",
                "layer": "access"
            },

            # End Devices
            "CSE-PC1": {
                "type": "host",
                "department": "CSE"
            },

            "IT-PC1": {
                "type": "host",
                "department": "IT"
            },

            "AI-PC1": {
                "type": "host",
                "department": "AI"
            },

            "ECE-PC1": {
                "type": "host",
                "department": "ECE"
            },

            "EEE-PC1": {
                "type": "host",
                "department": "EEE"
            },

            "ADMIN-PC1": {
                "type": "host",
                "department": "ADMIN"
            },

            "LIB-PC1": {
                "type": "host",
                "department": "LIBRARY"
            },

            "LAB-PC1": {
                "type": "host",
                "department": "LAB"
            }
        }

        for name, attributes in devices.items():

            self.graph.add_node(
                name,
                **attributes,
                status="active"
            )

        links = [

            # Core redundancy
            ("CORE-R1", "CORE-R2", 2),

            # Core to Distribution
            ("CORE-R1", "DIST-R1", 3),
            ("CORE-R1", "DIST-R2", 3),

            ("CORE-R2", "DIST-R3", 3),
            ("CORE-R2", "DIST-R4", 3),

            # Distribution redundancy
            ("DIST-R1", "DIST-R2", 2),
            ("DIST-R2", "DIST-R3", 2),
            ("DIST-R3", "DIST-R4", 2),
            ("DIST-R4", "DIST-R1", 2),

            # Distribution to Access
            ("DIST-R1", "SW-CSE", 1),
            ("DIST-R1", "SW-IT", 1),

            ("DIST-R2", "SW-AI", 1),
            ("DIST-R2", "SW-ECE", 1),

            ("DIST-R3", "SW-EEE", 1),
            ("DIST-R3", "SW-ADMIN", 1),

            ("DIST-R4", "SW-LIB", 1),
            ("DIST-R4", "SW-LAB", 1),

            # Redundant access connections
            ("DIST-R2", "SW-CSE", 4),
            ("DIST-R3", "SW-ECE", 4),
            ("DIST-R4", "SW-ADMIN", 4),
            ("DIST-R1", "SW-LIB", 4),

            # Hosts
            ("SW-CSE", "CSE-PC1", 1),
            ("SW-IT", "IT-PC1", 1),
            ("SW-AI", "AI-PC1", 1),
            ("SW-ECE", "ECE-PC1", 1),
            ("SW-EEE", "EEE-PC1", 1),
            ("SW-ADMIN", "ADMIN-PC1", 1),
            ("SW-LIB", "LIB-PC1", 1),
            ("SW-LAB", "LAB-PC1", 1)
        ]

        for source, destination, cost in links:

            self.graph.add_edge(
                source,
                destination,
                cost=cost,
                status="active"
            )

    def get_graph(self):

        return self.graph