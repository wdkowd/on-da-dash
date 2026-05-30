const tabs = document.querySelectorAll(".tab");
const tabImage = document.getElementById("tabImage");

tabs.forEach(tab => {
    tab.addEventListener("click", () => {

        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");

        const imagePath = tab.dataset.image;

        tabImage.src =
            imagePath + "?t=" + new Date().getTime();
    });
});

// Refresh top image every 30 seconds
setInterval(() => {
    const mainImage =
        document.getElementById("mainImage");

    mainImage.src =
        "images/ZZ.png?t=" +
        new Date().getTime();

}, 30000);