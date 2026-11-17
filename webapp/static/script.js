const SYMBOL_EMOJI = {
  CHERRY: "🍒",
  LEMON: "🍋",
  ORANGE: "🍊",
  PLUM: "🍇",
  BAR: "BAR",
  SEVEN: "7️⃣",
  WILD: "🃏",
  SCATTER: "💰",
};

const NUM_REELS = 5;
const NUM_ROWS = 3;
const STARTING_BALANCE = 100;

let balance = STARTING_BALANCE;

const gridEl = document.getElementById("grid");
const balanceEl = document.getElementById("balance");
const lastWinEl = document.getElementById("last-win");
const messageEl = document.getElementById("message");
const spinBtn = document.getElementById("spin-btn");
const resetBtn = document.getElementById("reset-btn");
const betSelect = document.getElementById("bet-select");
const fsPanel = document.getElementById("free-spins-panel");
const fsRemainingEl = document.getElementById("fs-remaining");
const fsTotalEl = document.getElementById("fs-total");

function buildGridCells() {
  gridEl.innerHTML = "";
  const cells = [];
  for (let row = 0; row < NUM_ROWS; row++) {
    const rowCells = [];
    for (let reel = 0; reel < NUM_REELS; reel++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      gridEl.appendChild(cell);
      rowCells.push(cell);
    }
    cells.push(rowCells);
  }
  return cells;
}

const cellEls = buildGridCells();

function renderGrid(grid, winningPositions) {
  winningPositions = winningPositions || new Set();
  for (let row = 0; row < NUM_ROWS; row++) {
    for (let reel = 0; reel < NUM_REELS; reel++) {
      const symbol = grid[reel][row];
      const cell = cellEls[row][reel];
      cell.textContent = SYMBOL_EMOJI[symbol] || symbol;
      cell.classList.toggle("bar-symbol", symbol === "BAR");
      cell.classList.toggle("win", winningPositions.has(reel + "," + row));
    }
  }
}

function winningPositionsFromResult(spinResult) {
  const positions = new Set();
  for (const win of spinResult.win_lines) {
    for (const pos of win.positions) {
      positions.add(pos[0] + "," + pos[1]);
    }
  }
  return positions;
}

function randomSymbol() {
  const symbols = Object.keys(SYMBOL_EMOJI);
  return symbols[Math.floor(Math.random() * symbols.length)];
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function spinAnimation(durationMs) {
  return new Promise((resolve) => {
    const interval = setInterval(() => {
      for (let row = 0; row < NUM_ROWS; row++) {
        for (let reel = 0; reel < NUM_REELS; reel++) {
          cellEls[row][reel].classList.remove("win");
          cellEls[row][reel].classList.remove("bar-symbol");
          cellEls[row][reel].textContent = SYMBOL_EMOJI[randomSymbol()];
        }
      }
    }, 60);
    setTimeout(() => {
      clearInterval(interval);
      resolve();
    }, durationMs);
  });
}

function setBalance(value) {
  balance = value;
  balanceEl.textContent = balance.toFixed(2);
}

function setMessage(text) {
  messageEl.textContent = text;
}

async function playFreeSpins(freeSpins) {
  fsPanel.classList.remove("hidden");
  setMessage(freeSpins.spins_played + " Free Spins Awarded!");
  await sleep(1200);

  let remaining = freeSpins.spins_played;
  let runningTotal = 0;

  for (const spinResult of freeSpins.spin_results) {
    fsRemainingEl.textContent = remaining;
    await spinAnimation(450);
    renderGrid(spinResult.grid, winningPositionsFromResult(spinResult));
    runningTotal += spinResult.total_payout;
    fsTotalEl.textContent = runningTotal.toFixed(2);
    remaining -= 1;
    await sleep(400);
  }

  const retriggerNote = freeSpins.retriggers > 0 ? " (" + freeSpins.retriggers + " retrigger" + (freeSpins.retriggers > 1 ? "s" : "") + ")" : "";
  setMessage("Bonus complete" + retriggerNote + "! Bonus win: " + freeSpins.total_payout.toFixed(2));
  await sleep(1600);
  fsPanel.classList.add("hidden");
}

async function spin() {
  const bet = parseFloat(betSelect.value);
  if (bet > balance) {
    setMessage("Not enough balance for this bet.");
    return;
  }

  spinBtn.disabled = true;
  setMessage("");
  lastWinEl.textContent = "0.00";
  setBalance(balance - bet);

  await spinAnimation(700);

  let data;
  try {
    const response = await fetch("/api/spin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bet: bet }),
    });
    if (!response.ok) {
      throw new Error("spin request failed");
    }
    data = await response.json();
  } catch (err) {
    setMessage("Error contacting server.");
    spinBtn.disabled = false;
    return;
  }

  renderGrid(data.base_spin.grid, winningPositionsFromResult(data.base_spin));

  if (data.base_spin.total_payout > 0) {
    setMessage("Win: " + data.base_spin.total_payout.toFixed(2));
  }

  if (data.free_spins) {
    await sleep(800);
    await playFreeSpins(data.free_spins);
  }

  lastWinEl.textContent = data.total_payout.toFixed(2);
  setBalance(balance + data.total_payout);
  spinBtn.disabled = false;
}

spinBtn.addEventListener("click", spin);
resetBtn.addEventListener("click", () => {
  setBalance(STARTING_BALANCE);
  setMessage("Balance reset.");
});

setBalance(STARTING_BALANCE);
renderGrid([
  ["CHERRY", "LEMON", "PLUM"],
  ["ORANGE", "BAR", "SEVEN"],
  ["CHERRY", "LEMON", "PLUM"],
  ["ORANGE", "BAR", "SEVEN"],
  ["CHERRY", "LEMON", "PLUM"],
]);
