document.addEventListener("DOMContentLoaded", function () {
    // Trova il tag script che include questo file
    const scriptTag = document.querySelector("script[src*='title_icons.js']");
    
    // Ottieni il path alla root dal data-attribute oppure calcola automaticamente
    const rootPath = scriptTag.getAttribute("data-root") || scriptTag.getAttribute("src").substring(0, scriptTag.getAttribute("src").lastIndexOf("/") + 1);

    // Funzione per ottenere l'icona della stagione attuale
    function getSeasonIcon(root) {
        const month = new Date().getMonth();
        let iconFile;

        if (month >= 2 && month <= 4) {
            iconFile = "spring.ico"; // Primavera (Mar-Mag)
        } else if (month >= 5 && month <= 7) {
            iconFile = "summer.ico"; // Estate (Giu-Ago)
        } else if (month >= 8 && month <= 10) {
            iconFile = "fall.ico"; // Autunno (Set-Nov)
        } else {
            iconFile = "winter.ico"; // Inverno (Dic-Feb)
        }

        // Crea o aggiorna il tag <link> per l'icona
        let link = document.querySelector("link[rel='icon']");
        if (!link) {
            link = document.createElement("link");
            link.rel = "icon";
            document.head.appendChild(link);
        }
        link.href = root + "icons/" + iconFile;
    }

    // Imposta l'icona
    getSeasonIcon(rootPath);
});
