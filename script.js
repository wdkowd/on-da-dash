let tabs = [];
let currentTab = null;

// -----------------------------
// LIVE IMAGE REFRESH
// -----------------------------
function refreshImage() {
    const img = document.getElementById("liveImage");
    img.src = "/images/ZZ.png?t=" + Date.now();
}
setInterval(refreshImage, 2000);


// -----------------------------
// LOAD DASH TABS
// -----------------------------
async function loadTabs() {
    const res = await fetch("/api/dash-tabs");
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
// SELECT DASH TAB
// -----------------------------
function selectTab(file, tabElement) {
    currentTab = file;

    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    tabElement.classList.add("active");

    document.getElementById("dashFrame").src =
        "/graphs/overwatch/" + file + "?t=" + Date.now();
}


// -----------------------------
// MODAL ELEMENTS
// -----------------------------
const modal = document.getElementById("modal");
const optsFrame = document.getElementById("optsFrame");


// -----------------------------
// BUTTON: REFRESH + OPEN OPTS
// -----------------------------
document.getElementById("optsBtn").onclick = async () => {
    try {
        // 1. Tell server to regenerate opts files
        const refreshRes = await fetch("/api/refresh-opts", {
            method: "POST"
        });

        const refreshData = await refreshRes.json();

        if (!refreshData.success) {
            alert("Failed to refresh opts");
            return;
        }

        // 2. Get updated file list
        const fileRes = await fetch("/api/opts-files");
        const files = await fileRes.json();

        if (files.length === 0) {
            alert("No opts files found");
            return;
        }

        // 3. Load newest file
        const file = files[0];

        optsFrame.src =
            "/graphs/opts/" + file + "?t=" + Date.now();

        // 4. Open modal
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