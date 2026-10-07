from flask import Flask, render_template, jsonify, request

from network.topology import CampusTopology
from network.routing import RoutingEngine
from network.failure_detector import FailureDetector
from network.self_healing import SelfHealingController
from network.packet_simulator import PacketSimulator
from network.ip_manager import IPAddressManager


app = Flask(__name__)

topology = CampusTopology()
graph = topology.get_graph()

ip_manager = IPAddressManager(graph)
ip_manager.assign_ip_addresses()

routing_engine = RoutingEngine(graph)

failure_detector = FailureDetector(graph)

self_healing = SelfHealingController(
    graph,
    routing_engine,
    failure_detector
)

packet_simulator = PacketSimulator(
    graph,
    routing_engine
)

simulation_history = []

last_failure = None
last_recovery = None
last_packet = None


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def normalize_algorithm(algorithm):

    if not algorithm:
        return "link_state"

    value = algorithm.lower().strip()

    if (
        value == "distance_vector"
        or "distance vector" in value
        or "bellman" in value
    ):
        return "distance_vector"

    return "link_state"


def calculate_route(source, destination, algorithm):

    algorithm = normalize_algorithm(algorithm)

    if algorithm == "distance_vector":

        return routing_engine.distance_vector_route(
            source,
            destination
        )

    return routing_engine.link_state_route(
        source,
        destination
    )


def get_failures():

    failed_devices = []

    for node, data in graph.nodes(data=True):

        if data.get("status") != "active":
            failed_devices.append(node)

    failed_links = []

    for source, destination, data in graph.edges(data=True):

        if data.get("status") != "active":

            failed_links.append({
                "source": source,
                "destination": destination
            })

    return {
        "failed_devices": failed_devices,
        "failed_links": failed_links
    }


def add_history(event_type, message, **extra):

    event = {
        "type": event_type,
        "message": message
    }

    event.update(extra)

    simulation_history.append(event)


# ==========================================================
# WEB PAGES
# ==========================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/simulation")
def simulation():
    return render_template("simulation.html")


@app.route("/recovery")
def recovery():
    return render_template("recovery.html")


@app.route("/packet")
def packet():
    return render_template("packet.html")


@app.route("/results")
def results():
    return render_template("results.html")


# ==========================================================
# TOPOLOGY
# ==========================================================

@app.route("/api/topology")
def get_topology():

    nodes = []

    for node, data in graph.nodes(data=True):

        nodes.append({
            "id": node,
            "type": data.get("type"),
            "layer": data.get("layer"),
            "department": data.get("department"),
            "status": data.get("status"),
            "ip_address": data.get("ip_address"),
            "subnet": data.get("subnet")
        })

    links = []

    for source, destination, data in graph.edges(data=True):

        links.append({
            "id": f"{source}-{destination}",
            "source": source,
            "target": destination,
            "cost": data.get("cost"),
            "status": data.get("status")
        })

    return jsonify({
        "nodes": nodes,
        "links": links
    })


# ==========================================================
# STATUS
# ==========================================================

@app.route("/api/status")
def get_status():

    failures = get_failures()

    status = "NORMAL"

    if (
        failures["failed_devices"]
        or failures["failed_links"]
    ):
        status = "FAILURE DETECTED"

    return jsonify({
        "status": status,
        "failed_devices": failures["failed_devices"],
        "failed_links": failures["failed_links"],
        "total_nodes": graph.number_of_nodes(),
        "total_links": graph.number_of_edges()
    })


# ==========================================================
# ROUTING
# ==========================================================

@app.route("/api/route")
def calculate_route_api():

    source = request.args.get("source")
    destination = request.args.get("destination")
    algorithm = request.args.get(
        "algorithm",
        "link_state"
    )

    if not source or not destination:

        return jsonify({
            "success": False,
            "message": "Source and destination are required"
        }), 400

    result = calculate_route(
        source,
        destination,
        algorithm
    )

    add_history(
        "ROUTING",
        result.get(
            "message",
            "Route calculated"
        ),
        source=source,
        destination=destination,
        algorithm=result.get("algorithm"),
        path=result.get("path", []),
        cost=result.get("cost")
    )

    return jsonify(result)


# ==========================================================
# DEVICE FAILURE
# ==========================================================

@app.route(
    "/api/failure/device",
    methods=["POST"]
)
def fail_device():

    global last_failure
    global last_recovery

    data = request.get_json() or {}

    device = data.get("device")
    source = data.get("source")
    destination = data.get("destination")
    algorithm = data.get(
        "algorithm",
        "link_state"
    )

    if not device:

        return jsonify({
            "success": False,
            "message": "Device is required"
        }), 400

    if device not in graph:

        return jsonify({
            "success": False,
            "message": "Device does not exist"
        }), 404

    # Calculate original route BEFORE failure
    original_route = None

    if source and destination:

        original_route = calculate_route(
            source,
            destination,
            algorithm
        )

    # Apply failure
    graph.nodes[device]["status"] = "failed"

    last_failure = {
        "type": "device",
        "device": device,
        "source": source,
        "destination": destination,
        "algorithm": normalize_algorithm(algorithm),
        "status": "failure_detected"
    }

    add_history(
        "FAILURE",
        f"Device {device} failed",
        component=device
    )

    # Calculate recovery route AFTER failure
    recovery_route = None

    if source and destination:

        recovery_route = calculate_route(
            source,
            destination,
            algorithm
        )

        last_recovery = {
            "status": (
                "recovered"
                if recovery_route["success"]
                else "failed"
            ),
            "failure": last_failure,
            "recovery": {
                "status": (
                    "recovered"
                    if recovery_route["success"]
                    else "failed"
                ),
                "source": source,
                "destination": destination,
                "path": recovery_route.get(
                    "path",
                    []
                ),
                "cost": recovery_route.get(
                    "cost"
                ),
                "algorithm": recovery_route.get(
                    "algorithm"
                ),
                "message": (
                    "Alternate route calculated successfully"
                    if recovery_route["success"]
                    else "No alternate route available"
                )
            },
            "original_route": original_route,
            "message": (
                "Alternate route calculated successfully"
                if recovery_route["success"]
                else "No alternate route available"
            )
        }

        add_history(
            "RECOVERY",
            last_recovery["message"],
            path=recovery_route.get(
                "path",
                []
            ),
            cost=recovery_route.get(
                "cost"
            )
        )

    return jsonify({
        "success": True,
        "failure": last_failure,
        "original_route": original_route,
        "recovery": last_recovery
    })


# ==========================================================
# LINK FAILURE
# ==========================================================

@app.route(
    "/api/failure/link",
    methods=["POST"]
)
def fail_link():

    global last_failure
    global last_recovery

    data = request.get_json() or {}

    source = data.get("source")
    destination = data.get("destination")

    route_source = data.get(
        "route_source"
    )

    route_destination = data.get(
        "route_destination"
    )

    algorithm = data.get(
        "algorithm",
        "link_state"
    )

    if not source or not destination:

        return jsonify({
            "success": False,
            "message": "Link source and destination are required"
        }), 400

    if not graph.has_edge(
        source,
        destination
    ):

        return jsonify({
            "success": False,
            "message": "Link does not exist"
        }), 404

    # Original route BEFORE failure
    original_route = None

    if route_source and route_destination:

        original_route = calculate_route(
            route_source,
            route_destination,
            algorithm
        )

    # Apply link failure
    graph[source][destination]["status"] = "failed"

    last_failure = {
        "type": "link",
        "source": source,
        "destination": destination,
        "route_source": route_source,
        "route_destination": route_destination,
        "algorithm": normalize_algorithm(algorithm),
        "status": "failure_detected"
    }

    add_history(
        "LINK FAILURE",
        f"Link {source} → {destination} failed",
        component=f"{source} → {destination}"
    )

    recovery_route = None

    if route_source and route_destination:

        recovery_route = calculate_route(
            route_source,
            route_destination,
            algorithm
        )

        last_recovery = {
            "status": (
                "recovered"
                if recovery_route["success"]
                else "failed"
            ),
            "failure": last_failure,
            "recovery": {
                "status": (
                    "recovered"
                    if recovery_route["success"]
                    else "failed"
                ),
                "source": route_source,
                "destination": route_destination,
                "path": recovery_route.get(
                    "path",
                    []
                ),
                "cost": recovery_route.get(
                    "cost"
                ),
                "algorithm": recovery_route.get(
                    "algorithm"
                ),
                "message": (
                    "Alternate route calculated successfully"
                    if recovery_route["success"]
                    else "No alternate route available"
                )
            },
            "original_route": original_route,
            "message": (
                "Alternate route calculated successfully"
                if recovery_route["success"]
                else "No alternate route available"
            )
        }

        add_history(
            "RECOVERY",
            last_recovery["message"],
            path=recovery_route.get(
                "path",
                []
            ),
            cost=recovery_route.get(
                "cost"
            )
        )

    return jsonify({
        "success": True,
        "failure": last_failure,
        "original_route": original_route,
        "recovery": last_recovery
    })


# ==========================================================
# RECOVER DEVICE
# ==========================================================

@app.route(
    "/api/recover/device",
    methods=["POST"]
)
def recover_device():

    data = request.get_json() or {}

    device = data.get("device")

    if device not in graph:

        return jsonify({
            "success": False,
            "message": "Device does not exist"
        }), 404

    graph.nodes[device]["status"] = "active"

    add_history(
        "RECOVERY",
        f"Device {device} recovered",
        component=device
    )

    return jsonify({
        "success": True,
        "device": device,
        "status": "ACTIVE"
    })


# ==========================================================
# RECOVER LINK
# ==========================================================

@app.route(
    "/api/recover/link",
    methods=["POST"]
)
def recover_link():

    data = request.get_json() or {}

    source = data.get("source")
    destination = data.get("destination")

    if not graph.has_edge(
        source,
        destination
    ):

        return jsonify({
            "success": False,
            "message": "Link does not exist"
        }), 404

    graph[source][destination]["status"] = "active"

    add_history(
        "RECOVERY",
        f"Link {source} → {destination} recovered",
        component=f"{source} → {destination}"
    )

    return jsonify({
        "success": True,
        "source": source,
        "destination": destination,
        "status": "ACTIVE"
    })


# ==========================================================
# RESET NETWORK
# ==========================================================

@app.route("/api/reset", methods=["POST"])
def reset_network():

    global last_failure
    global last_recovery
    global last_packet

    for node in graph.nodes:
        graph.nodes[node]["status"] = "active"

    for source, destination in graph.edges:
        graph[source][destination]["status"] = "active"

    simulation_history.clear()

    last_failure = None
    last_recovery = None
    last_packet = None

    return jsonify({
        "success": True,
        "message": "Network reset successfully"
    })


# ==========================================================
# RECOVERY ANALYSIS
# ==========================================================

@app.route("/api/recovery-analysis")
def recovery_analysis():

    return jsonify({
        "failure": last_failure,
        "recovery": last_recovery
    })


# ==========================================================
# PACKET SIMULATION
# ==========================================================

@app.route(
    "/api/packet",
    methods=["POST"]
)
def simulate_packet():

    global last_packet

    data = request.get_json() or {}

    source = data.get("source")
    destination = data.get("destination")

    protocol = data.get(
        "protocol",
        "TCP"
    )

    message = data.get(
        "message",
        "Hello Campus Network"
    )

    algorithm = data.get(
        "algorithm",
        "link_state"
    )

    if not source or not destination:

        return jsonify({
            "success": False,
            "message": "Source and destination are required"
        }), 400

    source_ip = ip_manager.get_ip(
        source
    )

    destination_ip = ip_manager.get_ip(
        destination
    )

    route = calculate_route(
        source,
        destination,
        algorithm
    )

    packet = packet_simulator.create_packet(

        source=source,

        destination=destination,

        data=message,

        source_ip=source_ip,

        destination_ip=destination_ip,

        protocol=protocol,

        source_port=5000,

        destination_port=80
    )

    if not route["success"]:

        packet["status"] = "failed"

        packet["logs"].append(
            "No route available"
        )

        last_packet = packet

        add_history(
            "PACKET",
            f"Packet {packet['packet_id']} failed: No route available"
        )

        return jsonify(packet)

    packet = packet_simulator.start_transmission(
        packet,
        route["path"]
    )

    last_packet = packet

    add_history(
        "PACKET",
        f"Packet {packet['packet_id']} {packet['status']}",
        packet_id=packet["packet_id"],
        source=source,
        destination=destination,
        protocol=protocol,
        hop_count=packet["hop_count"],
        reroute_count=packet["reroute_count"]
    )

    return jsonify(packet)


# ==========================================================
# DEVICE INFORMATION
# ==========================================================

@app.route(
    "/api/device/<device>"
)
def device_information(device):

    if device not in graph:

        return jsonify({
            "success": False,
            "message": "Device not found"
        }), 404

    data = graph.nodes[device]

    return jsonify({

        "device": device,

        "type":
            data.get("type"),

        "layer":
            data.get("layer"),

        "department":
            data.get("department"),

        "status":
            data.get("status"),

        "ip_address":
            data.get("ip_address"),

        "subnet":
            data.get("subnet")
    })


# ==========================================================
# SIMULATION HISTORY
# ==========================================================

@app.route("/api/history")
def get_history():

    return jsonify({
        "history": simulation_history
    })


# ==========================================================
# LAST PACKET
# ==========================================================

@app.route("/api/packet-last")
def get_last_packet():

    return jsonify({
        "packet": last_packet
    })


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )