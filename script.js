const API_URL = "https://condo-life-appointed-watches.trycloudflare.com";

let lastUpdate = 0;
let currentTabFile = null;

const mainImage = document.getElementById("mainImage");

const dashFrame =
    document.getElementById("dashFrame");

const modal =
    document.getElementById("plotModal");

const iframe =
    document.getElementById("plotFrame");

const openPlotBtn =
    document.getElementById("openPlotBtn");

const closeModal =
    document.getElementById("closeModal");


// ----------------------------------
// MAIN IMAGE
// ----------------------------------

function loadMainImage() {

    mainImage.src =
        `${API_URL}/image/ZZ.png?t=${Date.now()}`;

}


// ----------------------------------
// DASHBOARD HTML
// ----------------------------------

function loadDashGraph() {

    if (!currentTabFile)
        return;

    dashFrame.src =
        `${API_URL}/dash/${currentTabFile}?t=${Date.now()}`;

}


// ----------------------------------
// BUILD TABS
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
            document.getElementById("tabs");

        tabsContainer.innerHTML = "";

        if (!files.length)
            return;

        currentTabFile =
            files[0];

        files.forEach(
            (file, index) => {

                const button =
                    document.createElement("button");

                button.className =
                    "tab";

                if (index === 0)
                    button.classList.add("active");

                button.textContent =
                    file.replace("_dash.html", "");

                button.onclick =
                    () => {

                        document
                            .querySelectorAll(".tab")
                            .forEach(
                                t => t.classList.remove("active")
                            );

                        button.classList.add("active");

                        currentTabFile =
                            file;

                        loadDashGraph();

                    };

                tabsContainer.appendChild(button);

            }
        );

        loadDashGraph();

    }
    catch(error) {

        console.error(
            "Failed to build tabs",
            error
        );

    }

}


// ----------------------------------
// STATUS CHECK
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

            loadDashGraph();

        }

    }
    catch(error) {

        console.error(error);

    }

}


// ----------------------------------
// OPEN OPTS
// ----------------------------------

openPlotBtn.onclick =
    async () => {

        if (!currentTabFile)
            return;

        const tabNumber =
            currentTabFile.split("_")[0];

        openPlotBtn.disabled = true;
        openPlotBtn.textContent = "...";

        try {

            const response =
                await fetch(
                    `${API_URL}/generate_plot/${tabNumber}`,
                    {
                        method: "POST"
                    }
                );

            const result =
                await response.json();

            if (!result.success)
                throw new Error();

            iframe.src =
                `${API_URL}/plot/${tabNumber}_opts.html?t=${Date.now()}`;

            modal.style.display =
                "block";

        }
        catch(error) {

            console.error(error);

        }
        finally {

            openPlotBtn.disabled = false;
            openPlotBtn.textContent = "Os";

        }

    };


// ----------------------------------
// CLOSE MODAL
// ----------------------------------

closeModal.onclick =
    () => {

        modal.style.display = "none";
        iframe.src = "";

    };

window.onclick =
    event => {

        if (event.target === modal) {

            modal.style.display = "none";
            iframe.src = "";

        }

    };


// ----------------------------------
// STARTUP
// ----------------------------------

async function initialize() {

    await buildTabs();

    loadMainImage();

    setInterval(
        checkForUpdates,
        2000
    );

}

initialize();