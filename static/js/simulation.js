let networkData = null;

let cy = null;

let selectedRoute = [];

let lastRouteResult = null;

let recoveryRoute = [];

let simulationLogs = [];

const STORAGE_KEY = "campusNetworkSimulation";


document.addEventListener(
    "DOMContentLoaded",
    initializeSimulation
);


async function initializeSimulation() {

    loadSavedState();

    await loadTopology();

    setupFailureType();

    restoreSelectors();

    updateStatus();

}


function getSavedState() {

    return {

        failureType:
            document.getElementById("failureType")?.value || "",

        failureDevice:
            document.getElementById("failureDevice")?.value || "",

        failureLinkSource:
            document.getElementById("failureLinkSource")?.value || "",

        failureLinkDestination:
            document.getElementById("failureLinkDestination")?.value || "",

        routeSource:
            document.getElementById("routeSource")?.value || "",

        routeDestination:
            document.getElementById("routeDestination")?.value || "",

        routeAlgorithm:
            document.getElementById("routeAlgorithm")?.value || "",

        selectedRoute:
            selectedRoute,

        lastRouteResult:
            lastRouteResult,

        recoveryRoute:
            recoveryRoute,

        simulationLogs:
            simulationLogs

    };

}


function saveState() {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(getSavedState())
    );

}


function loadSavedState() {

    const saved =
        localStorage.getItem(
            STORAGE_KEY
        );

    if (!saved) {
        return;
    }

    try {

        const state =
            JSON.parse(saved);

        if (
            document.getElementById("failureType") &&
            state.failureType
        ) {

            document.getElementById(
                "failureType"
            ).value =
                state.failureType;

        }

        if (
            document.getElementById("routeAlgorithm") &&
            state.routeAlgorithm
        ) {

            document.getElementById(
                "routeAlgorithm"
            ).value =
                state.routeAlgorithm;

        }

        selectedRoute =
            Array.isArray(state.selectedRoute)
                ? state.selectedRoute
                : [];

        lastRouteResult =
            state.lastRouteResult || null;

        recoveryRoute =
            Array.isArray(state.recoveryRoute)
                ? state.recoveryRoute
                : [];

        simulationLogs =
            Array.isArray(state.simulationLogs)
                ? state.simulationLogs
                : [];

    } catch (error) {

        console.error(
            "Saved state error:",
            error
        );

        selectedRoute = [];
        lastRouteResult = null;
        recoveryRoute = [];
        simulationLogs = [];

    }

}
function restoreSimulationState() {

    const routeResult =
        document.getElementById(
            "routeResult"
        );

    const eventLog =
        document.getElementById(
            "eventLog"
        );

    if (
        lastRouteResult &&
        lastRouteResult.success &&
        selectedRoute.length > 1
    ) {

        displayRoute(
            lastRouteResult,
            false
        );

        highlightRoute(
            selectedRoute,
            "route"
        );

    }

    if (
        recoveryRoute.length > 1
    ) {

        highlightRoute(
            recoveryRoute,
            "recovery-route"
        );

    }

    if (
        eventLog &&
        simulationLogs.length
    ) {

        eventLog.innerHTML = "";

        simulationLogs.forEach(
            log => {

                const entry =
                    document.createElement(
                        "div"
                    );

                entry.className =
                    "event-entry";

                entry.innerHTML = `

                    <span class="event-type">
                        ${log.type}
                    </span>

                    <span>
                        ${log.message}
                    </span>

                `;

                eventLog.appendChild(
                    entry
                );

            }
        );

    }

}

async function loadTopology() {

    try {

        const response =
            await fetch("/api/topology");

        networkData =
            await response.json();

        populateSelectors();

        drawTopology();

        updateStatistics();

        restoreSimulationState();

    } catch (error) {

        console.error(
            "Topology loading error:",
            error
        );

    }

}


function populateSelectors() {

    const saved =
        getStoredState();


    const selectors = [

        "failureDevice",
        "failureLinkSource",
        "failureLinkDestination",
        "routeSource",
        "routeDestination"

    ];


    selectors.forEach(
        selectorId => {

            const select =
                document.getElementById(
                    selectorId
                );

            if (!select) {
                return;
            }


            const oldValue =
                saved[selectorId] || "";


            select.innerHTML =
                `<option value="">
                    Select device
                </option>`;


            networkData.nodes.forEach(
                node => {

                    const option =
                        document.createElement(
                            "option"
                        );

                    option.value =
                        node.id;

                    option.textContent =
                        node.id;

                    select.appendChild(
                        option
                    );

                }
            );


            if (
                oldValue &&
                [...select.options].some(
                    option =>
                        option.value === oldValue
                )
            ) {

                select.value =
                    oldValue;

            }

        }
    );

}


function getStoredState() {

    const saved =
        localStorage.getItem(
            STORAGE_KEY
        );

    if (!saved) {
        return {};
    }

    try {

        return JSON.parse(saved);

    } catch {

        return {};

    }

}


function restoreSelectors() {

    const state =
        getStoredState();


    Object.keys(state).forEach(
        key => {

            const element =
                document.getElementById(key);

            if (
                element &&
                state[key] !== undefined
            ) {

                element.value =
                    state[key];

            }

        }
    );


    setupFailureType();

}


function setupFailureType() {

    const failureType =
        document.getElementById(
            "failureType"
        );

    if (!failureType) {
        return;
    }


    failureType.onchange =
        function () {

            const deviceControls =
                document.getElementById(
                    "deviceFailureControls"
                );

            const linkControls =
                document.getElementById(
                    "linkFailureControls"
                );


            if (
                this.value === "link"
            ) {

                deviceControls.style.display =
                    "none";

                linkControls.style.display =
                    "block";

            } else {

                deviceControls.style.display =
                    "block";

                linkControls.style.display =
                    "none";

            }


            saveState();

        };


    failureType.dispatchEvent(
        new Event("change")
    );

}

function drawTopology() {

    const elements = [];

    networkData.nodes.forEach(node => {
        elements.push({
            data: {
                id: node.id,
                label: node.id,
                type: node.type,
                status: node.status
            }
        });
    });

    networkData.links.forEach(link => {
        elements.push({
            data: {
                id: link.id,
                source: link.source,
                target: link.target,
                cost: link.cost,
                status: link.status
            }
        });
    });

    const positions = {

        "CORE-R1": { x: 420, y: 80 },
        "CORE-R2": { x: 760, y: 80 },

        "DIST-R1": { x: 280, y: 220 },
        "DIST-R2": { x: 500, y: 220 },
        "DIST-R3": { x: 680, y: 220 },
        "DIST-R4": { x: 900, y: 220 },

        "SW-CSE": { x: 180, y: 390 },
        "SW-IT": { x: 320, y: 390 },
        "SW-AI": { x: 470, y: 390 },
        "SW-ECE": { x: 610, y: 390 },
        "SW-EEE": { x: 750, y: 390 },
        "SW-ADMIN": { x: 890, y: 390 },
        "SW-LIB": { x: 1030, y: 390 },
        "SW-LAB": { x: 1170, y: 390 },

        "CSE-PC1": { x: 180, y: 520 },
        "IT-PC1": { x: 320, y: 520 },
        "AI-PC1": { x: 470, y: 520 },
        "ECE-PC1": { x: 610, y: 520 },
        "EEE-PC1": { x: 750, y: 520 },
        "ADMIN-PC1": { x: 890, y: 520 },
        "LIB-PC1": { x: 1030, y: 520 },
        "LAB-PC1": { x: 1170, y: 520 }

    };

    if (cy) {
        cy.destroy();
    }

    cy = cytoscape({

        container: document.getElementById("networkGraph"),

        elements: elements,

        layout: {
            name: "preset",

            positions: function(node) {
                return positions[node.id()] || {
                    x: 600,
                    y: 300
                };
            },

            fit: true,
            padding: 50
        },

        style: [

            {
                selector: "node",

                style: {

                    "background-color": function(node) {

                        if (node.data("status") !== "active") {
                            return "#ef4444";
                        }

                        if (node.data("type") === "router") {
                            return "#0ea5e9";
                        }

                        if (node.data("type") === "switch") {
                            return "#8b5cf6";
                        }

                        return "#64748b";

                    },

                    "label": "data(label)",

                    "color": "#e2e8f0",

                    "font-size": "10px",

                    "font-weight": "bold",

                    "text-valign": "bottom",

                    "text-margin-y": "9px",

                    "text-outline-color": "#07111f",

                    "text-outline-width": 3,

                    "width": 30,

                    "height": 30,

                    "border-width": 2,

                    "border-color": function(node) {

                        if (node.data("status") !== "active") {
                            return "#ff4d4d";
                        }

                        if (node.data("type") === "router") {
                            return "#38bdf8";
                        }

                        if (node.data("type") === "switch") {
                            return "#c4b5fd";
                        }

                        return "#94a3b8";

                    }

                }

            },

            {
                selector: "edge",

                style: {

                    "width": 2,

                    "line-color": function(edge) {

                        if (edge.data("status") !== "active") {
                            return "#ef4444";
                        }

                        const cost = Number(edge.data("cost"));

                        if (cost === 1) {
                            return "#22c55e";
                        }

                        if (cost === 2) {
                            return "#38bdf8";
                        }

                        if (cost === 3) {
                            return "#f59e0b";
                        }

                        if (cost === 4) {
                            return "#a78bfa";
                        }

                        return "#64748b";

                    },

                    "label": "",

                    "color": "#f8fafc",

                    "font-size": "13px",

                    "font-weight": "bold",

                    "text-background-color": "#07111f",

                    "text-background-opacity": 1,

                    "text-background-padding": "5px",

                    "text-border-color": "#38bdf8",

                    "text-border-width": 1,

                    "text-border-opacity": 0.8,

                    "curve-style": "bezier",

                    "line-cap": "round"

                }

            },

            {
                selector: ".route",

                style: {

                    "width": 5

                }

            },

            {
                selector: ".recovery-route",

                style: {

                    "line-color": "#f59e0b",

                    "width": 5

                }

            },

            {
                selector: ".failed",

                style: {

                    "background-color": "#ef4444",

                    "line-color": "#ef4444",

                    "width": 5

                }

            }

        ]

    });

    cy.on("tap", "node", event => {

        const node = event.target;

        showNodeInfo(node.data());

    });

}


async function calculateRoute() {

    const source =
        document.getElementById(
            "routeSource"
        ).value;


    const destination =
        document.getElementById(
            "routeDestination"
        ).value;


    const algorithm =
        document.getElementById(
            "routeAlgorithm"
        ).value;


    saveState();


    if (
        !source ||
        !destination
    ) {

        addLog(
            "ERROR",
            "Select source and destination."
        );

        return;

    }


    if (source === destination) {

        addLog(
            "ERROR",
            "Source and destination cannot be the same."
        );

        return;

    }


    const response =
        await fetch(
            `/api/route?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}&algorithm=${algorithm}`
        );


    const result =
        await response.json();


    displayRoute(result);


    if (result.success) {

        highlightRoute(
            result.path,
            "route"
        );

    }


    addLog(
        "ROUTING",
        result.success
            ? `${result.algorithm}: ${result.path.join(" → ")} | Cost: ${result.cost}`
            : result.message
    );

}


function displayRoute(
    result,
    save = true
) {

    const output =
        document.getElementById(
            "routeResult"
        );

    if (!result.success) {

        output.innerHTML = `

            <div class="route-failed">

                NO ROUTE AVAILABLE

                <br><br>

                ${result.message}

            </div>

        `;

        selectedRoute = [];

        lastRouteResult = result;

        if (save) {
            saveState();
        }

        return;

    }

    selectedRoute =
        result.path;

    lastRouteResult =
        result;

    const edgeCosts = [];

    for (
        let i = 0;
        i < result.path.length - 1;
        i++
    ) {

        const source =
            result.path[i];

        const target =
            result.path[i + 1];

        const link =
            networkData.links.find(
                edge =>
                    (
                        edge.source === source &&
                        edge.target === target
                    ) ||
                    (
                        edge.source === target &&
                        edge.target === source
                    )
            );

        if (link) {

            edgeCosts.push(
                Number(link.cost)
            );

        }

    }

    const calculatedTotal =
        edgeCosts.reduce(
            (sum, cost) =>
                sum + cost,
            0
        );

    output.innerHTML = `

        <div class="route-success">

            <div>

                <span>
                    ALGORITHM
                </span>

                <strong>
                    ${result.algorithm}
                </strong>

            </div>

            <div>

                <span>
                    PATH
                </span>

                <strong>
                    ${result.path.join(" → ")}
                </strong>

            </div>

            <div>

                <span>
                    EDGE COST
                </span>

                <strong>
                    ${edgeCosts.join(" + ")}
                </strong>

            </div>

            <div>

                <span>
                    TOTAL COST
                </span>

                <strong>
                    ${calculatedTotal}
                </strong>

            </div>

        </div>

    `;

    if (save) {
        saveState();
    }

}


function highlightRoute(
    path,
    className
) {

    if (!cy) {
        return;
    }


    cy.elements()
        .removeClass(
            className
        );


    for (
        let i = 0;
        i < path.length - 1;
        i++
    ) {

        const source =
            path[i];

        const target =
            path[i + 1];


        const edge =
            cy.edges(
                `[source="${source}"][target="${target}"],
                 [source="${target}"][target="${source}"]`
            );


        edge.addClass(
            className
        );

    }

}


async function failSelectedDevice() {

    const device =
        document.getElementById(
            "failureDevice"
        ).value;


    const source =
        document.getElementById(
            "routeSource"
        ).value;


    const destination =
        document.getElementById(
            "routeDestination"
        ).value;


    const algorithm =
        document.getElementById(
            "routeAlgorithm"
        ).value;


    saveState();


    if (!device) {

        addLog(
            "ERROR",
            "Select a device to fail."
        );

        return;

    }


    const response =
        await fetch(
            "/api/failure/device",
            {

                method:
                    "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify({

                        device:
                            device,

                        source:
                            source,

                        destination:
                            destination,

                        algorithm:
                            algorithm

                    })

            }
        );


    const result =
        await response.json();


    if (!result.success) {

        addLog(
            "ERROR",
            result.message
        );

        return;

    }


    addLog(
        "FAILURE",
        `${device} has failed.`
    );


    await updateTopology();

    await updateStatus();


    if (
        result.recovery &&
        result.recovery.recovery &&
        result.recovery.recovery.path
    ) {

        const recovery =
            result.recovery.recovery;


        recoveryRoute = recovery.path;

saveState();

highlightRoute(
    recoveryRoute,
    "recovery-route"
);


        addLog(
            "SELF-HEALING",
            `Alternate route: ${recovery.path.join(" → ")} | Cost: ${recovery.cost}`
        );

    }


    if (
        result.original_route &&
        result.original_route.path
    ) {

        addLog(
            "ORIGINAL ROUTE",
            result.original_route.path.join(" → ")
        );

    }

}


async function failSelectedLink() {

    const source =
        document.getElementById(
            "failureLinkSource"
        ).value;


    const destination =
        document.getElementById(
            "failureLinkDestination"
        ).value;


    const routeSource =
        document.getElementById(
            "routeSource"
        ).value;


    const routeDestination =
        document.getElementById(
            "routeDestination"
        ).value;


    const algorithm =
        document.getElementById(
            "routeAlgorithm"
        ).value;


    saveState();


    if (
        !source ||
        !destination
    ) {

        addLog(
            "ERROR",
            "Select both link endpoints."
        );

        return;

    }


    const response =
        await fetch(
            "/api/failure/link",
            {

                method:
                    "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify({

                        source:
                            source,

                        destination:
                            destination,

                        route_source:
                            routeSource,

                        route_destination:
                            routeDestination,

                        algorithm:
                            algorithm

                    })

            }
        );


    const result =
        await response.json();


    if (!result.success) {

        addLog(
            "ERROR",
            result.message
        );

        return;

    }


    addLog(
        "LINK FAILURE",
        `${source} → ${destination} has failed.`
    );


    await updateTopology();

    await updateStatus();


    if (
        result.recovery &&
        result.recovery.recovery &&
        result.recovery.recovery.path
    ) {

        const recovery =
            result.recovery.recovery;


        recoveryRoute = recovery.path;

saveState();

highlightRoute(
    recoveryRoute,
    "recovery-route"
);


        addLog(
            "SELF-HEALING",
            `Alternate route: ${recovery.path.join(" → ")} | Cost: ${recovery.cost}`
        );

    }

}


async function updateTopology() {

    const saved =
        getSavedState();


    const response =
        await fetch(
            "/api/topology"
        );


    networkData =
        await response.json();


    if (cy) {
        cy.destroy();
    }


    drawTopology();

    populateSelectors();


    Object.keys(saved).forEach(
        key => {

            const element =
                document.getElementById(
                    key
                );

            if (
                element &&
                saved[key] !== undefined
            ) {

                element.value =
                    saved[key];

            }

        }
    );


    setupFailureType();

    updateStatistics();
    if (selectedRoute.length > 1) {
    highlightRoute(
        selectedRoute,
        "route"
    );
}

if (recoveryRoute.length > 1) {
    highlightRoute(
        recoveryRoute,
        "recovery-route"
    );
}

}


async function updateStatus() {

    const response =
        await fetch(
            "/api/status"
        );


    const status =
        await response.json();


    const badge =
        document.getElementById(
            "networkStatus"
        );


    if (
        status.failed_devices.length ||
        status.failed_links.length
    ) {

        badge.textContent =
            "● FAILURE DETECTED";

        badge.className =
            "status-badge failed";

    }

    else {

        badge.textContent =
            "● NETWORK NORMAL";

        badge.className =
            "status-badge normal";

    }


    document.getElementById(
        "failedCount"
    ).textContent =
        status.failed_devices.length +
        status.failed_links.length;

}


function updateStatistics() {

    document.getElementById(
        "nodeCount"
    ).textContent =
        networkData.nodes.length;


    document.getElementById(
        "linkCount"
    ).textContent =
        networkData.links.length;

}


function showNodeInfo(data) {

    addLog(
        "DEVICE",
        `${data.id} | ${data.type} | ${data.status}`
    );

}


function addLog(
    type,
    message
) {

    simulationLogs.unshift({
        type: type,
        message: message
    });

    saveState();

    const log =
        document.getElementById(
            "eventLog"
        );

    if (!log) {
        return;
    }

    const entry =
        document.createElement(
            "div"
        );

    entry.className =
        "event-entry";

    entry.innerHTML = `

        <span class="event-type">
            ${type}
        </span>

        <span>
            ${message}
        </span>

    `;

    log.prepend(
        entry
    );

}


async function resetNetwork() {

    const confirmed = confirm(
        "Reset the campus network? All failures, routes, selections and logs will be cleared."
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            "/api/reset",
            {
                method: "POST"
            }
        );

        const result = await response.json();

        if (!result.success) {

            alert(
                result.message ||
                "Network reset failed."
            );

            return;
        }


        /* Clear saved browser state */

        localStorage.removeItem(STORAGE_KEY);


        /* Clear selected route */

        selectedRoute = [];
        lastRouteResult = null;

recoveryRoute = [];

simulationLogs = [];

        /* Clear Route Analysis */

        const routeResult =
            document.getElementById("routeResult");

        if (routeResult) {

            routeResult.innerHTML = `
                <div class="empty-state">
                    Select source and destination
                    to calculate a route.
                </div>
            `;

        }


        /* Clear Live Event Log */

        const eventLog =
            document.getElementById("eventLog");

        if (eventLog) {
            eventLog.innerHTML = "";
        }


        /* Reset failure controls */

        const failureType =
            document.getElementById("failureType");

        const failureDevice =
            document.getElementById("failureDevice");

        const failureLinkSource =
            document.getElementById("failureLinkSource");

        const failureLinkDestination =
            document.getElementById("failureLinkDestination");

        const routeSource =
            document.getElementById("routeSource");

        const routeDestination =
            document.getElementById("routeDestination");

        const routeAlgorithm =
            document.getElementById("routeAlgorithm");


        if (failureType) {
            failureType.value = "device";
        }

        if (failureDevice) {
            failureDevice.value = "";
        }

        if (failureLinkSource) {
            failureLinkSource.value = "";
        }

        if (failureLinkDestination) {
            failureLinkDestination.value = "";
        }

        if (routeSource) {
            routeSource.value = "";
        }

        if (routeDestination) {
            routeDestination.value = "";
        }

        if (routeAlgorithm) {
            routeAlgorithm.value = "link_state";
        }


        const deviceControls =
    document.getElementById("deviceFailureControls");

const linkControls =
    document.getElementById("linkFailureControls");

if (deviceControls) {
    deviceControls.style.display = "block";
}

if (linkControls) {
    linkControls.style.display = "none";
}


        /* Reload original topology */

        await updateTopology();


        /* Update network status */

        await updateStatus();


        /* Remove all visual route/failure highlighting */

        if (cy) {

            cy.elements()
                .removeClass("route")
                .removeClass("recovery-route")
                .removeClass("failed");

        }


        /* Make absolutely sure the log stays empty */

        if (eventLog) {
            eventLog.innerHTML = "";
        }

    } catch (error) {

        console.error(
            "Reset error:",
            error
        );

        alert(
            "Unable to reset the network."
        );

    }

}