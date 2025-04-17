// Costanti e riferimenti agli elementi DOM
const nicknameInput = document.getElementById('nicknameInput');
const addPlayerBtn = document.getElementById('addPlayerBtn');
const playersList = document.getElementById('playersList');
const playerCountSpan = document.getElementById('playerCount');
const nextBtn = document.getElementById('nextBtn');
const showPlayersBtn = document.getElementById('showPlayersBtn');
const errorMessage = document.getElementById('errorMessage');

const MIN_PLAYERS = 6;
const MAX_PLAYERS = 32;
let players = [];

// Funzione per impostare il background in base alla stagione attuale
function setSeasonBackground() {
    const now = new Date();
    const month = now.getMonth(); // 0 = Gennaio, 11 = Dicembre
    let season = 'winter'; // Default

    // Definizione semplice delle stagioni:
    // Primavera: Marzo, Aprile, Maggio
    // Estate: Giugno, Luglio, Agosto
    // Autunno: Settembre, Ottobre, Novembre
    // Inverno: Dicembre, Gennaio, Febbraio
    if (month >= 2 && month < 5) {
        season = 'spring';
    } else if (month >= 5 && month < 8) {
        season = 'summer';
    } else if (month >= 8 && month < 11) {
        season = 'fall';
    } else {
        season = 'winter';
    }
    // Imposta il background dinamico
    document.body.style.background = `url('./../images/${season}.png') no-repeat center center fixed`;
    document.body.style.backgroundSize = "cover";
}

// Funzione per aggiornare l'interfaccia
function updateUI() {
    // Svuota la lista corrente
    playersList.innerHTML = '';
    // Aggiungi ogni giocatore come elemento della lista
    players.forEach((player, index) => {
        const li = document.createElement('li');
        li.textContent = player;

        // Crea il bottone per la rimozione
        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Rimuovi';
        removeBtn.classList.add('remove-btn');
        removeBtn.onclick = () => removePlayer(index);

        li.appendChild(removeBtn);
        playersList.appendChild(li);
    });

    // Aggiorna il counter
    playerCountSpan.textContent = players.length;

    // Imposta la classe 'valid' o 'invalid' in base al numero di giocatori
    if (players.length >= MIN_PLAYERS && players.length <= MAX_PLAYERS) {
        playerCountSpan.classList.remove('invalid');
        playerCountSpan.classList.add('valid');
    } else {
        playerCountSpan.classList.remove('valid');
        playerCountSpan.classList.add('invalid');
    }

    // Abilita/disabilita i pulsanti in base ai limiti e allo stato dell'input
    addPlayerBtn.disabled = players.length >= MAX_PLAYERS || nicknameInput.value.trim() === "";
    nextBtn.disabled = players.length < MIN_PLAYERS;
}

// Funzione per aggiungere un giocatore
function addPlayer() {
    const nickname = nicknameInput.value.trim();
    if (nickname === '') {
        alert('Inserisci un nickname valido!');
        return;
    }
    if (players.some(p => p.toLowerCase() === nickname.toLowerCase())) {
        // Controllo extra come fallback
        alert('Nickname già presente!');
        return;
    }
    if (players.length >= MAX_PLAYERS) {
        alert('Numero massimo di giocatori raggiunto!');
        return;
    }
    players.push(nickname);
    nicknameInput.value = '';
    savePlayers();
    updateUI();
}

// Funzione per rimuovere un giocatore
function removePlayer(index) {
    if (players.length <= 0) return;
    players.splice(index, 1);
    savePlayers();
    updateUI();
}

// Funzione per validare il nickname inserito e controllare duplicati
function validateNickname() {
    const nickname = nicknameInput.value.trim();
    if (nickname !== "" && players.some(p => p.toLowerCase() === nickname.toLowerCase())) {
        errorMessage.textContent = "Nickname già presente!";
        addPlayerBtn.disabled = true;
    } else {
        errorMessage.textContent = "";
        // Riabilita il bottone solo se c'è un testo e non si è raggiunto il massimo dei giocatori
        addPlayerBtn.disabled = nickname === "" || players.length >= MAX_PLAYERS;
    }
}

// Salva i giocatori nel local storage
function savePlayers() {
    localStorage.setItem('players', JSON.stringify(players));
}

// Carica i giocatori dal local storage
function loadPlayers() {
    const storedPlayers = localStorage.getItem('players');
    if (storedPlayers) {
        players = JSON.parse(storedPlayers);
    }
}

// Event listeners
addPlayerBtn.addEventListener('click', addPlayer);

nicknameInput.addEventListener('keyup', (e) => {
    validateNickname();
    if (e.key === 'Enter' && !addPlayerBtn.disabled) {
        addPlayer();
    }
});

// Per aggiornare la validazione in caso di incolla o altri input
nicknameInput.addEventListener('input', validateNickname);

nextBtn.addEventListener('click', () => {
    // Salva prima di andare avanti
    savePlayers();
    // Redirige alla pagina tournament_display.html
    window.location.href = './../tournament_display/tournament_display.html';   
});

showPlayersBtn.addEventListener('click', () => {
    console.log("SIUM");
});

// Inizializza la pagina
document.addEventListener('DOMContentLoaded', () => {
    setSeasonBackground();
    loadPlayers();
    updateUI();
});
