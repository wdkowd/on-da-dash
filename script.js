const API_URL = "https://appropriate-zus-trustee-anyway.trycloudflare.com";

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

async function loadMainImage() {
    // mainImage.src = `${API_URL}/zz/ZZ.html?t=${Date.now()}`;
    mainImage.src = `${API_URL}/zz/ZZ.html`;
}

async function updateZZGraph() {

    try {
        const response = await fetch(
            `${API_URL}/zzgraph-data?t=${Date.now()}`
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        mainImage.contentWindow.postMessage(
            {
                type: "updateZZGraph",
                data: data
            },
            "*"
        );

    } catch (error) {
        console.error("Graph update failed:", error);
    }
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

async function updateDashGraph() {
    if (!currentTabFile)
        return;
    try {
        const response = await fetch(
            `${API_URL}/live-data/${currentTabFile}?t=${Date.now()}`
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        dashFrame.contentWindow.postMessage(
            {
                type: "updateLiveGraph",
                data: data
            },
            "*"
        );

    } catch (error) {
        console.error("Live Graph update failed:", error);
    }

    try {
        const response = await fetch(
            `${API_URL}/live-ldo/${currentTabFile}?t=${Date.now()}`
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        dashFrame.contentWindow.postMessage(
            {
                type: "updateLDOGraph",
                data: data
            },
            "*"
        );

    } catch (error) {
        console.error("LDO Graph update failed:", error);
    }
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

    setInterval(updateZZGraph, 2000);
    setInterval(updateDashGraph, 2000);


}

initialize();