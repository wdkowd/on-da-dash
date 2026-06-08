const API_URL = "https://under-bench-snow-boat.trycloudflare.com";
    // "http://localhost:8000";

let lastUpdate = 0;

let currentTabFile = null;

const mainImage =
    document.getElementById("mainImage");

const tabImage =
    document.getElementById("tabImage");

const modal =
    document.getElementById(
        "plotModal"
    );

const iframe =
    document.getElementById(
        "plotFrame"
    );

const openPlotBtn =
    document.getElementById(
        "openPlotBtn"
    );

const closeModal =
    document.getElementById(
        "closeModal"
    );

// ----------------------------------
// Load Main Dashboard Image (ZZ.png)
// ----------------------------------

function loadMainImage() {

    mainImage.src =
        `${API_URL}/image/ZZ.png?t=${Date.now()}`;
}


// ----------------------------------
// Load Selected Tab Image
// ----------------------------------

function loadTabImage() {

    if (!currentTabFile) {
        return;
    }

    tabImage.src =
        `${API_URL}/image/${currentTabFile}?t=${Date.now()}`;
}


// ----------------------------------
// Build Tabs Dynamically
// ----------------------------------

async function buildTabs() {

    try {

        const response =
            await fetch(
                `${API_URL}/tabs`
            );

        const data =
            await response.json();

        const files =
            data.files;

        const tabsContainer =
            document.getElementById(
                "tabs"
            );

        tabsContainer.innerHTML = "";

        if (files.length === 0) {
            return;
        }

        currentTabFile =
            files[0];

        files.forEach(
            (file, index) => {

                const button =
                    document.createElement(
                        "button"
                    );

                button.className =
                    "tab";

                if (index === 0) {
                    button.classList.add(
                        "active"
                    );
                }

                // Convert:
                // 1_imgL.png -> 1
                // 2_imgL.png -> 2

                button.textContent =
                    file.replace(
                        "_dripL.png",
                        ""
                    );

                button.onclick =
                    () => {

                        document
                            .querySelectorAll(
                                ".tab"
                            )
                            .forEach(
                                t =>
                                t.classList.remove(
                                    "active"
                                )
                            );

                        button.classList.add(
                            "active"
                        );

                        currentTabFile =
                            file;

                        loadTabImage();

                    };

                tabsContainer.appendChild(
                    button
                );

            }
        );

        loadTabImage();

    }
    catch(error) {

        console.error(
            "Failed to build tabs",
            error
        );

    }

}


// ----------------------------------
// Check For Image Updates
// ----------------------------------

async function checkForUpdates() {

    try {

        const response =
            await fetch(
                `${API_URL}/status`
            );

        const data =
            await response.json();

        if (
            data.last_update >
            lastUpdate
        ) {

            lastUpdate =
                data.last_update;

            loadMainImage();

            loadTabImage();

            console.log(
                "Images refreshed"
            );

        }

    }
    catch(error) {

        console.error(
            "Status check failed",
            error
        );

    }

}

// ----------------------------------
// Open Opts
// ----------------------------------
openPlotBtn.onclick =
    () => {

        if (!currentTabFile)
            return;

        const plotName =
            currentTabFile.replace(
                "_dripL.png",
                "_opts.html"
            );

        iframe.src =
            `${API_URL}/plot/${plotName}`;

        modal.style.display =
            "block";
    };
// ----------------------------------
// Close Opts
// ----------------------------------
closeModal.onclick =
    () => {

        modal.style.display =
            "none";

        iframe.src = "";
    };

window.onclick =
    event => {

        if (
            event.target === modal
        ) {

            modal.style.display =
                "none";

            iframe.src = "";
        }

    };
// ----------------------------------
// Startup
// ----------------------------------

async function initialize() {

    await buildTabs();

    loadMainImage();

    checkForUpdates();

    setInterval(
        checkForUpdates,
        2000
    );

}

initialize();