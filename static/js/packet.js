const PACKET_STORAGE_KEY =
    "campusNetworkPacket";


document.addEventListener(
    "DOMContentLoaded",
    loadDevices
);


async function loadDevices() {

    try {

        const response =
            await fetch(
                "/api/topology"
            );


        const data =
            await response.json();


        const sources = [

            "packetSource",

            "packetDestination"

        ];


        const saved =
            getPacketState();


        sources.forEach(
            id => {

                const select =
                    document.getElementById(
                        id
                    );


                if (!select) {
                    return;
                }


                data.nodes.forEach(
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
                    saved[id]
                ) {

                    select.value =
                        saved[id];

                }

            }
        );


        const protocol =
            document.getElementById(
                "packetProtocol"
            );


        const message =
            document.getElementById(
                "packetMessage"
            );


        if (
            protocol &&
            saved.packetProtocol
        ) {

            protocol.value =
                saved.packetProtocol;

        }


        if (
            message &&
            saved.packetMessage
        ) {

            message.value =
                saved.packetMessage;

        }


        setupPersistence();


    } catch (error) {

        console.error(
            "Unable to load devices:",
            error
        );

    }

}


function getPacketState() {

    const saved =
        localStorage.getItem(
            PACKET_STORAGE_KEY
        );


    if (!saved) {
        return {};
    }


    try {

        return JSON.parse(
            saved
        );

    } catch {

        return {};

    }

}


function savePacketState() {

    const state = {

        packetSource:
            document.getElementById(
                "packetSource"
            )?.value || "",

        packetDestination:
            document.getElementById(
                "packetDestination"
            )?.value || "",

        packetProtocol:
            document.getElementById(
                "packetProtocol"
            )?.value || "TCP",

        packetMessage:
            document.getElementById(
                "packetMessage"
            )?.value || ""

    };


    localStorage.setItem(
        PACKET_STORAGE_KEY,
        JSON.stringify(state)
    );

}


function setupPersistence() {

    const fields = [

        "packetSource",

        "packetDestination",

        "packetProtocol",

        "packetMessage"

    ];


    fields.forEach(
        id => {

            const element =
                document.getElementById(
                    id
                );


            if (!element) {
                return;
            }


            element.addEventListener(
                "change",
                savePacketState
            );


            element.addEventListener(
                "input",
                savePacketState
            );

        }
    );

}


async function sendPacket() {

    const source =
        document.getElementById(
            "packetSource"
        ).value;


    const destination =
        document.getElementById(
            "packetDestination"
        ).value;


    const protocol =
        document.getElementById(
            "packetProtocol"
        ).value;


    const message =
        document.getElementById(
            "packetMessage"
        ).value;


    if (!source || !destination) {

        alert(
            "Please select source and destination."
        );

        return;

    }


    if (
        source === destination
    ) {

        alert(
            "Source and destination cannot be the same."
        );

        return;

    }


    savePacketState();


    const response =
        await fetch(
            "/api/packet",
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify({

                        source,

                        destination,

                        protocol,

                        message

                    })

            }
        );


    const packet =
        await response.json();


    if (!response.ok) {

        console.error(
            packet
        );


        alert(
            packet.message ||
            "Packet transmission failed."
        );

        return;

    }


    displayPacket(
        packet
    );


    displayLogs(
        packet.logs || []
    );

}


function displayPacket(
    packet
) {

    const result =
        document.getElementById(
            "packetResult"
        );


    if (!result) {
        return;
    }


    result.innerHTML = `

        <div class="packet-header">

            <span>
                PACKET #${packet.packet_id}
            </span>

            <strong>
                ${packet.status.toUpperCase()}
            </strong>

        </div>


        <div class="packet-grid">


            <div>

                <span>
                    SOURCE
                </span>

                <strong>
                    ${packet.source}
                </strong>

            </div>


            <div>

                <span>
                    DESTINATION
                </span>

                <strong>
                    ${packet.destination}
                </strong>

            </div>


            <div>

                <span>
                    SOURCE IP
                </span>

                <strong>
                    ${packet.source_ip || "--"}
                </strong>

            </div>


            <div>

                <span>
                    DESTINATION IP
                </span>

                <strong>
                    ${packet.destination_ip || "--"}
                </strong>

            </div>


            <div>

                <span>
                    PROTOCOL
                </span>

                <strong>
                    ${packet.protocol}
                </strong>

            </div>


            <div>

                <span>
                    TTL
                </span>

                <strong>
                    ${packet.ttl}
                </strong>

            </div>


            <div>

                <span>
                    HOPS
                </span>

                <strong>
                    ${packet.hop_count}
                </strong>

            </div>


            <div>

                <span>
                    REROUTES
                </span>

                <strong>
                    ${packet.reroute_count}
                </strong>

            </div>


        </div>


        <div class="packet-path">

            <span>
                ROUTE
            </span>

            <p>

                ${
                    packet.path &&
                    packet.path.length
                        ? packet.path.join(
                            " → "
                        )
                        : "No route available"
                }

            </p>

        </div>

    `;

}


function displayLogs(
    logs
) {

    const container =
        document.getElementById(
            "packetLogs"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    logs.forEach(
        log => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "packet-log";


            item.textContent =
                log;


            container.appendChild(
                item
            );

        }
    );

}


async function resetNetwork() {

    const confirmed =
        confirm(
            "Reset the campus network? All failures, recovery data and saved selections will be cleared."
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/reset",
                {
                    method: "POST"
                }
            );


        const result =
            await response.json();


        if (!result.success) {

            alert(
                result.message ||
                "Network reset failed."
            );

            return;

        }


        localStorage.removeItem(
            PACKET_STORAGE_KEY
        );


        localStorage.removeItem(
            "campusNetworkSimulation"
        );


        window.location.href =
            "/simulation";

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