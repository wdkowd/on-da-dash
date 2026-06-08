const API_URL = "https://adaptive-definition-jason-ship.trycloudflare.com";
    // "http://localhost:8000";

// -----------------------------
// LIVE IMAGE REFRESH
// -----------------------------
function refreshImage() {
    const img = document.getElementById("liveImage");
    img.src = `${API_URL}/images/ZZ.png?t=` + Date.now();
}
setInterval(refreshImage, 2000);


// -----------------------------
// STATE
// -----------------------------
let tabs = [];
let currentTab = null;


// -----------------------------
// LOAD DASH TABS
// -----------------------------
async function loadTabs() {
    const res = await fetch(`${API_URL}/api/dash-tabs`);
    tabs = await res.json();

    const tabBar = document.getElementById("tabBar");

    tabs.forEach((file, idx) => {
        const tab = document.createElement("div");
        tab.className = "tab";
        tab.innerText = file.replace("_dash.html", "");

        tab.onclick = () => selectTab(file, tab);

        tabBar.appendChild(tab);

        if (idx === 0) {
            selectTab(file, tab);
        }
    });
}


// -----------------------------
// SELECT TAB
// -----------------------------
function selectTab(file, tabElement) {
    currentTab = file;

    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    tabElement.classList.add("active");

    document.getElementById("dashFrame").src =
        `${API_URL}/graphs/overwatch/` + file + "?t=" + Date.now();
}


// -----------------------------
// MODAL ELEMENTS
// -----------------------------
const modal = document.getElementById("modal");
const optsFrame = document.getElementById("optsFrame");


// -----------------------------
// OPTS BUTTON (REFRESH + LOAD)
// -----------------------------
document.getElementById("optsBtn").onclick = async () => {
    try {
        // 1. trigger server refresh
        const refreshRes = await fetch(`${API_URL}/api/refresh-opts`, {
            method: "POST"
        });

        const refreshData = await refreshRes.json();

        if (!refreshData.success) {
            alert("Failed to refresh opts");
            return;
        }

        // 2. get updated file list
        const fileRes = await fetch(`${API_URL}/api/opts-files`);
        const files = await fileRes.json();

        if (!files.length) {
            alert("No opts files found");
            return;
        }

        // 3. load newest file
        const file = files[0];

        optsFrame.src =
            `${API_URL}/graphs/opts/` + file + "?t=" + Date.now();

        // 4. open modal
        modal.style.display = "block";

    } catch (err) {
        console.error(err);
        alert("Error refreshing opts");
    }
};


// -----------------------------
// CLOSE MODAL
// -----------------------------
document.getElementById("closeModal").onclick = () => {
    modal.style.display = "none";
};

window.onclick = (e) => {
    if (e.target === modal) {
        modal.style.display = "none";
    }
};


// -----------------------------
// INIT
// -----------------------------
loadTabs();