/**
 * Costanti e gestione del local storage per lo stato del torneo
 */
const BRACKET_KEY = 'tournamentData';
const PLAYERS_KEY = 'players';

/**
 * Imposta il background in base alla stagione attuale
 */
function setSeasonBackground() {
    const now = new Date();
    const month = now.getMonth(); // 0 = Gennaio, 11 = Dicembre
    let season = 'winter';
    if (month >= 2 && month < 5) {
        season = 'spring';
    } else if (month >= 5 && month < 8) {
        season = 'summer';
    } else if (month >= 8 && month < 11) {
        season = 'fall';
    }
    document.body.style.background = `url('./../images/${season}.png') no-repeat center center fixed`;
    document.body.style.backgroundSize = "cover";
}

/**
 * Salva e carica lo stato del torneo
 */
function saveTournament(data) {
    localStorage.setItem(BRACKET_KEY, JSON.stringify(data));
}

function loadTournament() {
    const data = localStorage.getItem(BRACKET_KEY);
    return data ? JSON.parse(data) : null;
}

/**
 * Funzione ausiliaria per randomizzare un array
 */
function shuffleArray(arr) {
    const lastElement = arr[arr.length - 1];
    const hasSpecialElement = lastElement.includes("???");

    if (hasSpecialElement) {
        const shuffled = arr.slice(0, -1).sort(() => Math.random() - 0.5);
        return [...shuffled, lastElement];
    } else {
        return arr.slice().sort(() => Math.random() - 0.5);
    }
}

/**
 * Genera i partecipanti iniziali.
 * Se i giocatori sono >= 12, crea squadre randomicamente,
 * altrimenti utilizza i singoli giocatori.
 */
function generateInitialParticipants(players) {
    // Randomizza sempre l'array dei giocatori
    const shuffled = players.slice().sort(() => Math.random() - 0.5);
    if (players.length >= 0) {
        const teams = [];
        for (let i = 0; i < shuffled.length; i += 2) {
            if (i + 1 < shuffled.length) {
                teams.push(`${shuffled[i]} & ${shuffled[i + 1]}`);
            } else {
                teams.push(`${shuffled[i]} & ???`);
            }
        }
        return teams;
    } else {
        return shuffled;
    }
}

/**
 * Genera il primo round a partire dai partecipanti.
 * Se il numero è dispari, l'ultimo viene accantonato.
 */
function generateInitialRound(participants) {
    const round = { matches: [], oddCompetitor: null, luckyLoser: null };
    const parts = participants.slice();

    if (parts.length % 2 === 1) {
        round.oddCompetitor = parts.pop();
    }

    while (parts.length > 0) {
        const comp1 = parts.shift();
        const comp2 = parts.shift();
        round.matches.push({
            id: 'm-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5),
            competitor1: comp1,
            competitor2: comp2,
            winner: null,
            isExtra: false
        });
    }

    if (round.oddCompetitor) {
        round.matches.push({
            id: 'extra-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5),
            competitor1: round.oddCompetitor,
            competitor2: "",
            winner: null,
            isExtra: true
        });
    }
    return round;
}

/**
 * Genera il round successivo a partire dai vincitori del round corrente
 */
function generateNextRound(currentRound) {
    const winners = getRoundWinners(currentRound);
    if (winners.length < 1) return null;

    const nextRound = { matches: [], oddCompetitor: null, luckyLoser: null };
    const parts = winners.slice();

    if (parts.length % 2 === 1) {
        nextRound.oddCompetitor = parts.pop();
    }
    while (parts.length > 0) {
        const comp1 = parts.shift();
        const comp2 = parts.shift();
        nextRound.matches.push({
            id: 'm-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5),
            competitor1: comp1,
            competitor2: comp2,
            winner: null,
            isExtra: false
        });
    }

    if (nextRound.oddCompetitor) {
        nextRound.matches.push({
            id: 'extra-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5),
            competitor1: nextRound.oddCompetitor,
            competitor2: "",
            winner: null,
            isExtra: true
        });
    }
    return nextRound;
}

/**
 * Restituisce i vincitori del round
 */
function getRoundWinners(round) {
    const winners = [];
    round.matches.forEach(match => {
        if (match.winner) winners.push(match.winner);
    });
    return winners;
}

/**
 * Restituisce il perdente di un match, se il vincitore è già stato selezionato
 */
function getMatchLoser(match) {
    if (!match.winner) return null;
    return match.winner === match.competitor1 ? match.competitor2 : match.competitor1;
}

/**
 * Attiva il bottone per il ripescaggio
 */
function processOddAndLuckyButton(round) {
    if (round.oddCompetitor) {
        const extraMatch = round.matches.find(m => m.isExtra);
        if (extraMatch) {
            const matchNotWonNotExtra = round.matches.some(m => !m.winner && !m.isExtra);
            const matchesExtraChosen = round.matches.some(m => m.isExtra && m.competitor2 !== "");
            document.getElementById('selectLuckyLoserBtn').disabled = matchNotWonNotExtra || matchesExtraChosen;
        }
    }
}

/**
 * Funzione per confrontare due array (ignorando l'ordine)
 */
function arraysEqual(a, b) {
    if (!Array.isArray(a) || !Array.isArray(b)) return false;
    if (a.length !== b.length) return false;
    const sortedA = a.slice().sort();
    const sortedB = b.slice().sort();
    return sortedA.join(',') === sortedB.join(',');
}


/**
 * Inizializzazione dello stato del torneo.
 * Se il torneo già esiste in local storage, viene confrontata la lista di nomi
 * (players) con quella salvata in tournament.originalPlayers.
 * Se sono diverse, il torneo viene ricreato.
 */
let tournament = loadTournament();
let players = JSON.parse(localStorage.getItem(PLAYERS_KEY)) || [];

if (tournament) {
    // Se la lista di giocatori è cambiata, ricrea il torneo
    if (!arraysEqual(tournament.originalPlayers, players)) {
        tournament = null;
    }
}

if (!tournament) {
    const initialTeams = generateInitialParticipants(players);
    const shuffledTeams = shuffleArray(initialTeams);
    const firstRound = generateInitialRound(shuffledTeams);
    tournament = {
        initialTeams: initialTeams,          // Squadre/partecipanti generati inizialmente
        originalPlayers: players,              // Lista dei giocatori con cui è stato creato il torneo
        rounds: [firstRound],
        currentRound: 0
    };
    saveTournament(tournament);
}

/**
 * Aggiorna l'interfaccia del bracket
 */
function updateBracketUI() {
    const bracketContainer = document.getElementById('bracketContainer');
    const lastRoundIndex = tournament.rounds.length - 1;

    // Crea o aggiorna i round
    tournament.rounds.forEach((round, roundIndex) => {
        const roundId = `round-${roundIndex}`;
        let roundDiv = document.getElementById(roundId);

        // Crea nuovo round se non esiste
        if (!roundDiv) {
            roundDiv = document.createElement('div');
            roundDiv.className = 'round';
            roundDiv.id = roundId;

            const title = document.createElement('h2');
            title.textContent = `Turno ${roundIndex + 1}`;
            roundDiv.appendChild(title);

            bracketContainer.appendChild(roundDiv);
        }

        // Aggiorna i match esistenti o creane nuovi
        round.matches.forEach((match, matchIndex) => {
            const matchId = `match-${match.id}`;
            let matchDiv = document.getElementById(matchId);

            if (!matchDiv) {
                // Crea nuovo elemento match
                matchDiv = document.createElement('div');
                matchDiv.className = 'match' + (match.isExtra ? ' extra' : '');
                matchDiv.id = matchId;

                const comp1Div = document.createElement('div');
                comp1Div.className = 'competitor';
                comp1Div.addEventListener('click', () => selectWinner(roundIndex, match.id, match.competitor1));

                const comp2Div = document.createElement('div');
                comp2Div.className = 'competitor';
                comp2Div.addEventListener('click', () => selectWinner(roundIndex, match.id, match.competitor2));

                matchDiv.appendChild(comp1Div);
                matchDiv.appendChild(comp2Div);
                roundDiv.appendChild(matchDiv);
            }

            // Aggiorna contenuti e classi
            const competitors = matchDiv.getElementsByClassName('competitor');
            competitors[0].textContent = match.competitor1;
            competitors[1].textContent = match.competitor2;

            competitors[0].classList.toggle('selected', match.winner === match.competitor1);
            competitors[1].classList.toggle('selected', match.winner === match.competitor2);
        });

        // Rimuovi match non più presenti (se necessario)
        const existingMatches = roundDiv.querySelectorAll('.match');
        existingMatches.forEach(existingMatch => {
            if (!round.matches.some(m => `match-${m.id}` === existingMatch.id)) {
                existingMatch.remove();
            }
        });

        if (roundIndex !== lastRoundIndex) {
            disableAllMatches(round)
        }
    });

    // Aggiorna lo stato dei pulsanti
    const currRound = tournament.rounds[tournament.currentRound];
    const allDecided = currRound.matches.every(match => match.winner !== null);
    const matchesExtraChosen = currRound.matches.some(m => m.isExtra && m.competitor2 !== "");
    document.getElementById('nextRoundBtn').disabled = !allDecided;
    processOddAndLuckyButton(currRound);
    if (matchesExtraChosen) {
        activateExtraMatchOnly(currRound)
    } else {
        disableExtraMatch(currRound)
    }
}

/**
 * Selezione del vincitore in un match.
 */
function selectWinner(roundIndex, matchId, selected) {
    const round = tournament.rounds[roundIndex];
    const match = round.matches.find(m => m.id === matchId);
    if (match) {
        match.winner = selected;
        processOddAndLuckyButton(round);
        saveTournament(tournament);
        updateBracketUI();
    }
}

/**
 * Attiva solo il match extra e disattiva gli altri
 */
function activateExtraMatchOnly(round) {
    round.matches.forEach(match => {
        const matchElement = document.getElementById(`match-${match.id}`);
        if (matchElement) {
            if (match.isExtra) {
                matchElement.classList.remove('disabled-match');
                matchElement.classList.add('active-extra');
            } else {
                matchElement.classList.remove('active-extra');
                matchElement.classList.add('disabled-match');
            }
        }
    });
}

/**
 * Attiva solo il match extra e disattiva gli altri
 */
function disableExtraMatch(round) {
    round.matches.forEach(match => {
        const matchElement = document.getElementById(`match-${match.id}`);
        if (matchElement) {
            if (match.isExtra) {
                matchElement.classList.remove('active-extra');
                matchElement.classList.add('disabled-match');
            }
        }
    });
}

/**
 * Disattiva tutti i match del turno corrente
 */
function disableAllMatches(round) {
    round.matches.forEach(match => {
        const matchElement = document.getElementById(`match-${match.id}`);
        if (matchElement) {
            if (match.isExtra) {
                matchElement.classList.remove('active-extra');
            }
            matchElement.classList.add('disabled-match')
        };
    });
}

/**
 * Gestione del pulsante "Prossimo Turno"
 */
document.getElementById('selectLuckyLoserBtn').addEventListener('click', () => {
    const currRound = tournament.rounds[tournament.currentRound];
    let losers = currRound.matches
        .map(getMatchLoser)
        .filter(loser => loser !== null);

    if (losers.length > 0) {
        let luckyLoser = losers[Math.floor(Math.random() * losers.length)];
        let extraMatch = currRound.matches.find(m => m.isExtra);
        if (extraMatch) {
            if (extraMatch.competitor1.includes("???")) {
                let potentialPlayers = losers.filter(l => l !== luckyLoser)
                    .flatMap(team => team.includes(" & ") ? team.split(" & ") : [team]);

                if (potentialPlayers.length > 0) {
                    let randomPlayer = potentialPlayers[Math.floor(Math.random() * potentialPlayers.length)];
                    extraMatch.competitor1 = extraMatch.competitor1.replace("???", randomPlayer);
                }
            }

            extraMatch.competitor2 = luckyLoser;
            activateExtraMatchOnly(currRound); // Attiva solo il match extra
            saveTournament(tournament);
            updateBracketUI();
        }
    }
});

/**
 * Gestione del pulsante "Prossimo Turno"
 */
document.getElementById('nextRoundBtn').addEventListener('click', () => {
    const currRound = tournament.rounds[tournament.currentRound];
    if (getRoundWinners(currRound).length === 1 && currRound.matches.length === 1) {
        alert("Torneo concluso! Vincitore: " + currRound.matches[0].winner);
        return;
    }
    const nextRound = generateNextRound(currRound);
    if (nextRound) {
        tournament.rounds.push(nextRound);
        tournament.currentRound++;
        disableAllMatches(currRound); // Disattiva tutti i match del turno attuale
        saveTournament(tournament);
        updateBracketUI();
    } else {
        alert("Errore nella generazione del turno successivo.");
    }
});

/**
 * Gestione del pulsante "Reset Torneo" (cancella tutto e ricarica la pagina)
 */
document.getElementById('resetTournamentBtn').addEventListener('click', () => {
    if (confirm("Sei sicuro di voler resettare il torneo?")) {
        localStorage.removeItem(BRACKET_KEY);
        window.location.reload();
    }
});

/**
 * Gestione del pulsante "Nuovo Torneo".
 * Se sono già state generate delle squadre (in tournament.initialTeams),
 * rigenera il primo round randomizzando l'ordine.
 */
document.getElementById('newTournamentBtn').addEventListener('click', () => {
    if (confirm("Vuoi iniziare un nuovo torneo con le stesse squadre?")) {
        if (tournament && tournament.initialTeams) {
            const shuffledTeams = shuffleArray(tournament.initialTeams);
            const firstRound = generateInitialRound(shuffledTeams);
            tournament.rounds = [firstRound];
            tournament.currentRound = 0;
            saveTournament(tournament);
            updateBracketUI();
        } else {
            localStorage.removeItem(BRACKET_KEY);
            window.location.reload();
        }
    }
});

/**
 * Inizializzazione
 */
document.addEventListener('DOMContentLoaded', () => {
    setSeasonBackground();
    updateBracketUI();
});
