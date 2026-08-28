const API_URL = "http://localhost:8000";

let lastUpdate = 0;
let currentTabFile = null;

const mainImage = 
    document.getElementById("mainImage");

const dashFrame =
    document.getElementById("dashFrame");

const modal =
    document.getElementById("plotModal");

const iframe =
    document.getElementById("plotFrame");

const openOptsPlotBtn =
    document.getElementById("openOptsPlotBtn");

const openLogOddsBtn =
    document.getElementById("openLogOddsBtn");

const openMnMxMaBtn =
    document.getElementById("openMnMxMaBtn");

const closeModal =
    document.getElementById("closeModal");

const menu_graphs = document.getElementById("menu_graphs");

const button_graphs = menu_graphs.querySelector(".dropbtn_graph");


// ----------------------------------
// MAIN IMAGE
// ----------------------------------

function loadMainImage() {
    mainImage.src =
        `${API_URL}/zz/ZZ.html?t=${Date.now()}`;
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

            // loadDashGraph();

        }

    }
    catch(error) {

        console.error(error);

    }

}

// ----------------------------------
// DROPDOWN
// ----------------------------------

button_graphs.addEventListener("click", (e) => {
    e.stopPropagation();
    menu_graphs.classList.toggle("active");
});

document.addEventListener("click", () => {
    menu_graphs.classList.remove("active");
});


// ----------------------------------
// OPEN OPTS
// ----------------------------------

openOptsPlotBtn.onclick =
    async () => {

        if (!currentTabFile)
            return;

        const tabNumber =
            currentTabFile.split("_")[0];

        openOptsPlotBtn.disabled = true;

        try {

            const response =
                await fetch(
                    `${API_URL}/generate_opts_plot/${tabNumber}`,
                    {
                        method: "POST"
                    }
                );

            const result =
                await response.json();

            if (!result.success)
                throw new Error();

            iframe.src =
                `${API_URL}/plotOpts/${tabNumber}_opts.html?t=${Date.now()}`;

            modal.style.display =
                "block";

        }
        catch(error) {

            console.error(error);

        }
        finally {

            openOptsPlotBtn.disabled = false;

        }

    };

// ----------------------------------
// OPEN LOGODDS
// ----------------------------------

openLogOddsBtn.onclick =
async () => {

    if (!currentTabFile)
        return;

    const tabNumber =
        currentTabFile.split("_")[0];

    openLogOddsBtn.disabled = true;

    try {
        iframe.src =
            `${API_URL}/plotLogOdds/${tabNumber}_LogOdds.html?t=${Date.now()}`;

        modal.style.display =
            "block";

    }
    catch(error) {

        console.error(error);

    }
    finally {

        openLogOddsBtn.disabled = false;

    }

};

// ----------------------------------
// OPEN MNMXMA BENCHMARK
// ----------------------------------

openMnMxMaBtn.onclick =
async () => {

    if (!currentTabFile)
        return;

    const tabNumber =
        currentTabFile.split("_")[0];

    openMnMxMaBtn.disabled = true;

    try {
        iframe.src =
            `${API_URL}/plotMnMxma/${tabNumber}_MnMxMa.html?t=${Date.now()}`;

        modal.style.display =
            "block";

    }
    catch(error) {

        console.error(error);

    }
    finally {

        openMnMxMaBtn.disabled = false;

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