let recoveryData = null;
let networkData = null;
let cy = null;


document.addEventListener(
    "DOMContentLoaded",
    loadRecovery
);


async function loadRecovery() {

    try {

        const recoveryResponse =
            await fetch(
                "/api/recovery-analysis"
            );


        const recoveryResult =
            await recoveryResponse.json();


        const topologyResponse =
            await fetch(
                "/api/topology"
            );


        networkData =
            await topologyResponse.json();


        const historyResponse =
            await fetch(
                "/api/history"
            );


        const historyResult =
            await historyResponse.json();


        recoveryData =
            recoveryResult;


        displayRecovery(
            recoveryResult
        );


        drawRecoveryTopology(
            recoveryResult
        );


        displayEventLog(
            historyResult.history || []
        );


    } catch (error) {

        console.error(
            "Recovery loading error:",
            error
        );

    }

}


/* ==========================================================
   RECOVERY INFORMATION
========================================================== */


function displayRecovery(data) {

    const failure =
        data.failure;


    const recoveryWrapper =
        data.recovery;


    if (
        !failure ||
        !recoveryWrapper
    ) {

        showNoRecovery();

        return;

    }


    const recovery =
        recoveryWrapper.recovery;


    if (!recovery) {

        showNoRecovery();

        return;

    }


    /* -----------------------------
       FAILURE
    ----------------------------- */

    if (
        failure.type === "device"
    ) {

        document.getElementById(
            "failureComponent"
        ).textContent =
            failure.device;


        document.getElementById(
            "failedItem"
        ).textContent =
            failure.device;

    }


    else if (
        failure.type === "link"
    ) {

        const link =
            `${failure.source} → ${failure.destination}`;


        document.getElementById(
            "failureComponent"
        ).textContent =
            link;


        document.getElementById(
            "failedItem"
        ).textContent =
            link;

    }


    document.getElementById(
        "failureStatus"
    ).textContent =
        "FAILURE DETECTED";


    /* -----------------------------
       ALGORITHM
    ----------------------------- */

    document.getElementById(
        "algorithm"
    ).textContent =
        recovery.algorithm ||
        "--";


    document.getElementById(
        "analysisAlgorithm"
    ).textContent =
        recovery.algorithm ||
        "--";


    /* -----------------------------
       COST
    ----------------------------- */

    const recoveryCost =
        recovery.cost;


    document.getElementById(
        "routeCost"
    ).textContent =
        recoveryCost !== null &&
        recoveryCost !== undefined
            ? recoveryCost
            : "--";


    document.getElementById(
        "analysisCost"
    ).textContent =
        recoveryCost !== null &&
        recoveryCost !== undefined
            ? recoveryCost
            : "--";


    /* -----------------------------
       STATUS
    ----------------------------- */

    document.getElementById(
        "recoveryStatus"
    ).textContent =
        (
            recovery.status ||
            recoveryWrapper.status ||
            "UNKNOWN"
        ).toUpperCase();


    /* -----------------------------
       ORIGINAL ROUTE
    ----------------------------- */

    const originalRoute =
        data.original_route ||
        recoveryWrapper.original_route;


    if (
        originalRoute &&
        originalRoute.path
    ) {

        document.getElementById(
            "originalRoute"
        ).textContent =
            originalRoute.path.join(
                " → "
            );

    }

    else {

        document.getElementById(
            "originalRoute"
        ).textContent =
            "No original route available";

    }


    /* -----------------------------
       RECOVERY ROUTE
    ----------------------------- */

    if (
        recovery.path &&
        recovery.path.length
    ) {

        document.getElementById(
            "recoveryRoute"
        ).textContent =
            recovery.path.join(
                " → "
            );


        document.getElementById(
            "analysisPath"
        ).textContent =
            recovery.path.join(
                " → "
            );


        document.getElementById(
            "analysisEndpoints"
        ).textContent =
            `${recovery.source} → ${recovery.destination}`;

    }

    else {

        document.getElementById(
            "recoveryRoute"
        ).textContent =
            "No alternate route available";


        document.getElementById(
            "analysisPath"
        ).textContent =
            "No alternate route available";

    }

}


/* ==========================================================
   DRAW TOPOLOGY
========================================================== */


function drawRecoveryTopology(
    recoveryResult
) {

    const elements = [];


    const positions = {

        "CORE-R1":
            { x: 420, y: 80 },

        "CORE-R2":
            { x: 760, y: 80 },


        "DIST-R1":
            { x: 280, y: 220 },

        "DIST-R2":
            { x: 500, y: 220 },

        "DIST-R3":
            { x: 680, y: 220 },

        "DIST-R4":
            { x: 900, y: 220 },


        "SW-CSE":
            { x: 180, y: 390 },

        "SW-IT":
            { x: 320, y: 390 },

        "SW-AI":
            { x: 470, y: 390 },

        "SW-ECE":
            { x: 610, y: 390 },

        "SW-EEE":
            { x: 750, y: 390 },

        "SW-ADMIN":
            { x: 890, y: 390 },

        "SW-LIB":
            { x: 1030, y: 390 },

        "SW-LAB":
            { x: 1170, y: 390 },


        "CSE-PC1":
            { x: 180, y: 520 },

        "IT-PC1":
            { x: 320, y: 520 },

        "AI-PC1":
            { x: 470, y: 520 },

        "ECE-PC1":
            { x: 610, y: 520 },

        "EEE-PC1":
            { x: 750, y: 520 },

        "ADMIN-PC1":
            { x: 890, y: 520 },

        "LIB-PC1":
            { x: 1030, y: 520 },

        "LAB-PC1":
            { x: 1170, y: 520 }

    };


    /* -----------------------------
       NODES
    ----------------------------- */

    networkData.nodes.forEach(
        node => {

            elements.push({

                data: {

                    id:
                        node.id,

                    label:
                        node.id,

                    type:
                        node.type,

                    status:
                        node.status

                }

            });

        }
    );


    /* -----------------------------
       LINKS
    ----------------------------- */

    networkData.links.forEach(
        link => {

            elements.push({

                data: {

                    id:
                        link.id,

                    source:
                        link.source,

                    target:
                        link.target,

                    cost:
                        link.cost,

                    status:
                        link.status

                }

            });

        }
    );


    if (cy) {

        cy.destroy();

    }


    cy =
        cytoscape({

            container:
                document.getElementById(
                    "networkGraph"
                ),

            elements:
                elements,


            layout: {

                name:
                    "preset",

                positions:
                    positions,

                fit:
                    true,

                padding:
                    50

            },


            style: [

                /* =========================
                   NODES
                ========================= */

                {

                    selector:
                        "node",

                    style: {

                        "background-color":
                            function(node) {

                                if (
                                    node.data(
                                        "status"
                                    ) !== "active"
                                ) {

                                    return "#ef4444";

                                }


                                if (
                                    node.data(
                                        "type"
                                    ) === "router"
                                ) {

                                    return "#38bdf8";

                                }


                                if (
                                    node.data(
                                        "type"
                                    ) === "switch"
                                ) {

                                    return "#a78bfa";

                                }


                                return "#94a3b8";

                            },


                        "label":
                            "data(label)",

                        "color":
                            "#e2e8f0",

                        "font-size":
                            "9px",

                        "font-weight":
                            "bold",

                        "text-valign":
                            "bottom",

                        "text-margin-y":
                            9,

                        "width":
                            28,

                        "height":
                            28,

                        "border-width":
                            2,

                        "border-color":
                            "#0f172a",

                        "overlay-opacity":
                            0

                    }

                },


                /* =========================
                   EDGES
                ========================= */

                {

                    selector:
                        "edge",

                    style: {

                        "width":
                            2,

                        "line-color":
                            function(edge) {

                                if (
                                    edge.data(
                                        "status"
                                    ) !== "active"
                                ) {

                                    return "#ef4444";

                                }


                                return "#31506b";

                            },


                        "label":
                            "data(cost)",

                        "color":
                            "#e2e8f0",

                        "font-size":
                            "13px",

                        "font-weight":
                            "bold",

                        "text-background-color":
                            "#07111f",

                        "text-background-opacity":
                            1,

                        "text-background-padding":
                            "4px",

                        "text-border-color":
                            "#38bdf8",

                        "text-border-width":
                            1,

                        "text-border-opacity":
                            0.7,

                        "curve-style":
                            "bezier"

                    }

                },


                /* =========================
                   ORIGINAL ROUTE
                ========================= */

                {

                    selector:
                        ".original-route",

                    style: {

                        "line-color":
                            "#22c55e",

                        "width":
                            4

                    }

                },


                /* =========================
                   RECOVERY ROUTE
                ========================= */

                {

                    selector:
                        ".recovery-route",

                    style: {

                        "line-color":
                            "#f59e0b",

                        "width":
                            5

                    }

                },


                /* =========================
                   FAILED
                ========================= */

                {

                    selector:
                        ".failed-element",

                    style: {

                        "line-color":
                            "#ef4444",

                        "background-color":
                            "#ef4444",

                        "width":
                            5

                    }

                }

            ]

        });


    applyRecoveryHighlight(
        recoveryResult
    );

}


/* ==========================================================
   HIGHLIGHT ROUTES
========================================================== */


function applyRecoveryHighlight(
    result
) {

    if (!cy) {
        return;
    }


    const original =
        result.original_route ||
        (
            result.recovery &&
            result.recovery.original_route
        );


    const recovery =
        result.recovery &&
        result.recovery.recovery;


    if (
        original &&
        original.path
    ) {

        highlightPath(
            original.path,
            "original-route"
        );

    }


    if (
        recovery &&
        recovery.path
    ) {

        highlightPath(
            recovery.path,
            "recovery-route"
        );

    }


    const failure =
        result.failure;


    if (!failure) {
        return;
    }


    if (
        failure.type === "device" &&
        failure.device
    ) {

        const node =
            cy.getElementById(
                failure.device
            );


        node.addClass(
            "failed-element"
        );

    }


    if (
        failure.type === "link"
    ) {

        const edge =
            cy.edges().filter(
                edge => {

                    return (
                        (
                            edge.data(
                                "source"
                            ) === failure.source &&
                            edge.data(
                                "target"
                            ) === failure.destination
                        )
                        ||
                        (
                            edge.data(
                                "source"
                            ) === failure.destination &&
                            edge.data(
                                "target"
                            ) === failure.source
                        )
                    );

                }
            );


        edge.addClass(
            "failed-element"
        );

    }

}


/* ==========================================================
   PATH HIGHLIGHT
========================================================== */


function highlightPath(
    path,
    className
) {

    if (
        !path ||
        path.length < 2
    ) {

        return;

    }


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
            cy.edges().filter(
                e => {

                    return (
                        (
                            e.data(
                                "source"
                            ) === source &&
                            e.data(
                                "target"
                            ) === target
                        )
                        ||
                        (
                            e.data(
                                "source"
                            ) === target &&
                            e.data(
                                "target"
                            ) === source
                        )
                    );

                }
            );


        edge.addClass(
            className
        );

    }

}


/* ==========================================================
   EVENT LOG
========================================================== */


function displayEventLog(
    history
) {

    const log =
        document.getElementById(
            "eventLog"
        );


    log.innerHTML = "";


    if (
        !history ||
        history.length === 0
    ) {

        log.innerHTML = `

            <div class="empty-state">
                No simulation events recorded.
            </div>

        `;

        return;

    }


    history
        .slice()
        .reverse()
        .forEach(
            event => {

                const entry =
                    document.createElement(
                        "div"
                    );


                entry.className =
                    "event-entry";


                entry.innerHTML = `

                    <span class="event-type">
                        ${event.type || "SYSTEM"}
                    </span>

                    <span>
                        ${event.message || ""}
                    </span>

                `;


                log.appendChild(
                    entry
                );

            }
        );

}