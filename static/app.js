// Front-end of the futures simulator.
//
// The browser keeps the settings and the list of moves played so far, and
// sends them to the server. The server replays the game in Python and sends
// back the table to display. Here we only show what the server sends.
//
// T (all the texts in the chosen language) and LANG are defined in index.html.

let fixed = null;       // numbers that never change: point_value, start_price, start_rate
let limits = null;      // allowed range of each setting
let defaults = null;    // default value of each setting
let settings = null;    // settings of the current game
let moves = [];         // moves played so far, like {change: 0.02, correlation: 1, noise: 0.3}
let lastData = null;    // last answer of the server
let flowChart = null;
let rateChart = null;
let balanceChart = null;
let tourStage = -1;     // -1 means the guided tour is not running

const GREEN = '#0ca30c';
const RED = '#d03b3b';
const BLUE = '#2a78d6';
const VIOLET = '#6250d6';

function $(id) {
  return document.getElementById(id);
}

// ---------------------------------------------------------------------------
// Text and number formatting
// ---------------------------------------------------------------------------
// Replace the {words} of a template by values: fill('Hi {name}', {name: 'Ann'})
function fill(template, values) {
  return template.replace(/\{(\w+)\}/g, (match, key) => values[key]);
}

function numberText(n, digits) {
  return n.toLocaleString(T.locale, { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function number(n) {
  return numberText(Math.round(n), 0);
}

function money(n) {
  const v = Math.round(n);
  const sign = v < 0 ? '−' : '';
  return sign + fill(T.money, { n: numberText(Math.abs(v), 0) });
}

function signedMoney(n) {
  const v = Math.round(n);
  const sign = v > 0 ? '+' : v < 0 ? '−' : '';
  return sign + fill(T.money, { n: numberText(Math.abs(v), 0) });
}

function percent(x, digits) {
  return fill(T.percent, { n: numberText(x, digits) });
}

function signedNumber(x, digits) {
  const sign = x > 0 ? '+' : x < 0 ? '−' : '';
  return sign + numberText(Math.abs(x), digits);
}

// ---------------------------------------------------------------------------
// Settings (the sliders and the long / short choice)
// ---------------------------------------------------------------------------
const SETTING_FORMATS = {
  volatility: (v) => percent(v, 1),
  rate_volatility: (v) => numberText(v, 2),
  steps: (v) => number(v),
  start_margin: (v) => money(v),
  maintenance_ratio: (v) => percent(v, 0),
};

function readSettings() {
  const result = {};
  document.querySelectorAll('[data-setting]').forEach((slider) => {
    result[slider.dataset.setting] = Number(slider.value);
  });
  result.position = document.querySelector('input[name=position]:checked').value;
  return result;
}

function showSettingValues() {
  document.querySelectorAll('[data-setting]').forEach((slider) => {
    const name = slider.dataset.setting;
    $('o-' + name).textContent = SETTING_FORMATS[name](Number(slider.value));
  });
}

// Put the given settings in the sliders and in the long / short choice.
function applySettings(values) {
  document.querySelectorAll('[data-setting]').forEach((slider) => {
    const name = slider.dataset.setting;
    if (values[name] !== undefined) {
      slider.value = values[name];
    }
  });
  const position = values.position === 'short' ? 'short' : 'long';
  document.querySelector('input[name=position][value=' + position + ']').checked = true;
  showSettingValues();
}

function setupSettings() {
  document.querySelectorAll('[data-setting]').forEach((slider) => {
    const name = slider.dataset.setting;
    slider.min = limits[name][0];
    slider.max = limits[name][1];
    slider.value = defaults[name];
    slider.addEventListener('input', showSettingValues);
    slider.addEventListener('change', settingsChanged);
  });
  document.querySelectorAll('input[name=position]').forEach((radio) => {
    radio.addEventListener('change', settingsChanged);
  });
  showSettingValues();
}

// Changing a setting starts a new game.
function settingsChanged() {
  exitTour();
  send([]);
}

// ---------------------------------------------------------------------------
// Correlation slider
// ---------------------------------------------------------------------------
function correlation() {
  return Number($('corr').value);
}

function showCorrelation() {
  const c = correlation();
  let label = T.corr_zero;
  if (c >= 0.3) label = T.corr_positive;
  if (c <= -0.3) label = T.corr_negative;
  $('corr-out').textContent = signedNumber(c, 1) + ' (' + label + ')';
}

// ---------------------------------------------------------------------------
// Talking to the server
// ---------------------------------------------------------------------------
function showMessage(text, isError) {
  $('msg').textContent = text;
  $('msg').classList.toggle('error', isError === true);
}

async function post(path, body) {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  return { ok: response.ok, data: data };
}

// Send a list of moves to the server and show the result. In a move, a change
// or a noise equal to null is replaced by a random number on the server.
async function send(newMoves) {
  const gameSettings = readSettings();
  try {
    const answer = await post('/api/play', { settings: gameSettings, moves: newMoves });
    if (!answer.ok) {
      showMessage(answer.data.error || T.server_error, true);
      return false;
    }
    settings = gameSettings;
    moves = answer.data.moves;
    lastData = answer.data;
    showGame(answer.data);
    return true;
  } catch (error) {
    showMessage(T.network_error, true);
    return false;
  }
}

function gameIsOver() {
  if (moves.length >= settings.steps) {
    showMessage(T.maturity);
    return true;
  }
  return false;
}

function sendStep(change) {
  if (gameIsOver()) return Promise.resolve(false);
  const move = { change: change, correlation: correlation(), noise: null };
  return send(moves.concat([move]));
}

function sendRemainingSteps() {
  if (gameIsOver()) return Promise.resolve(false);
  const allMoves = moves.slice();
  while (allMoves.length < settings.steps) {
    allMoves.push({ change: null, correlation: correlation(), noise: null });
  }
  return send(allMoves);
}

// ---------------------------------------------------------------------------
// Buttons
// ---------------------------------------------------------------------------
function clickStep(change) {
  exitTour();
  sendStep(change);
}

async function clickPlayToMaturity() {
  exitTour();
  const ok = await sendRemainingSteps();
  if (ok) showMessage(T.auto_done);
}

function clickUndo() {
  exitTour();
  send(moves.slice(0, -1));
}

function clickRestart() {
  exitTour();
  send([]);
}

async function clickMonteCarlo() {
  $('mc').innerHTML = '<p class="mc-title">' + T.mc_wait + '</p>';
  try {
    const answer = await post('/api/monte-carlo', { settings: readSettings(), paths: 2000 });
    if (!answer.ok) {
      $('mc').textContent = answer.data.error || T.server_error;
      return;
    }
    showMonteCarlo(answer.data);
  } catch (error) {
    $('mc').textContent = T.network_error;
  }
}

// ---------------------------------------------------------------------------
// Describing a step in words
// ---------------------------------------------------------------------------
function describe(data) {
  const rows = data.rows;
  if (rows.length === 0) {
    return fill(T.intro, {
      position: T['position_' + settings.position],
      point: money(fixed.point_value),
      start: money(settings.start_margin),
      maintenance: money(data.maintenance_margin),
    });
  }

  const row = rows[rows.length - 1];
  const gained = row.cash >= 0;
  const parts = [];

  parts.push(fill(T.step_head, {
    step: row.step,
    direction: row.change >= 0 ? T.rises : T.falls,
    pct: percent(Math.abs(row.change * 100), 1),
  }));

  if (gained) {
    parts.push(fill(T.step_gain, { amount: money(row.cash) }));
  } else {
    parts.push(fill(T.step_loss, { amount: money(-row.cash) }));
  }

  const rateMove = row.rate - row.old_rate;
  if (Math.abs(rateMove) < 0.005) {
    parts.push(fill(T.rate_flat, { rate: percent(row.rate, 2) }));
  } else {
    const rateRose = rateMove > 0;
    // Good for you: a gain invested at a higher rate, or a loss borrowed at a lower rate.
    const good = (gained === rateRose);
    parts.push(fill(T.rate_move, {
      direction: rateRose ? T.rises : T.falls,
      rate: percent(row.rate, 2),
      action: gained ? T.action_gain : T.action_loss,
      level: rateRose ? T.level_up : T.level_down,
      verdict: good ? T.verdict_good : T.verdict_bad,
    }));
  }

  if (row.margin_call > 0) {
    parts.push(fill(T.margin_call, {
      maintenance: money(data.maintenance_margin),
      amount: money(row.margin_call),
      start: money(settings.start_margin),
    }));
  }
  return parts.join(' ');
}

function describeGap(stepsPlayed, gap) {
  if (stepsPlayed < 2) return T.gap_few;
  if (gap > 0.5) return fill(T.gap_earned, { amount: money(gap) });
  if (gap < -0.5) return fill(T.gap_cost, { amount: money(-gap) });
  return T.gap_zero;
}

// ---------------------------------------------------------------------------
// Showing the result
// ---------------------------------------------------------------------------
function showGame(data) {
  const rows = data.rows;
  const last = rows.length > 0 ? rows[rows.length - 1] : null;

  // The four tiles
  $('t-n').textContent = rows.length + ' / ' + settings.steps;
  $('t-f').textContent = number(last ? last.price : fixed.start_price);
  $('t-r').textContent = percent(last ? last.rate : fixed.start_rate, 2);
  $('t-b').textContent = money(last ? last.balance : settings.start_margin);

  showMessage(describe(data));
  showCharts(data);
  showTable(rows);
  fillGuide(data);

  // Future vs forward
  $('r-fut').textContent = signedMoney(data.summary.future);
  $('r-fwd').textContent = signedMoney(data.summary.forward);
  $('r-diff').textContent = signedMoney(data.summary.gap);
  $('r-txt').textContent = describeGap(rows.length, data.summary.gap);
}

// Write the numbers inside the "How it works" guide.
function fillGuide(data) {
  const values = {
    start_price: fixed.start_price,
    point_value: fixed.point_value,
    start_margin: settings.start_margin,
    maintenance_margin: data.maintenance_margin,
    start_rate: fixed.start_rate,
  };
  document.querySelectorAll('[data-param]').forEach((element) => {
    const value = values[element.dataset.param];
    if (element.dataset.format === 'money') {
      element.textContent = money(value);
    } else if (element.dataset.format === 'percent') {
      element.textContent = percent(value, 1);
    } else {
      element.textContent = number(value);
    }
  });
}

// Fill a list with null until it has the wanted length (empty spots on a chart).
function padTo(list, length) {
  while (list.length < length) {
    list.push(null);
  }
  return list;
}

function showCharts(data) {
  const rows = data.rows;
  const steps = [];
  for (let i = 1; i <= settings.steps; i++) {
    steps.push(i);
  }
  const stepsFromZero = [0].concat(steps);

  // Cash flow of each step
  const cash = rows.map((row) => row.cash);
  const colors = cash.map((c) => (c >= 0 ? GREEN : RED));
  flowChart.data.labels = steps;
  flowChart.data.datasets[0].data = padTo(cash, settings.steps);
  flowChart.data.datasets[0].backgroundColor = colors;
  flowChart.update('none');

  // Interest rate
  const rates = [fixed.start_rate].concat(rows.map((row) => row.rate));
  rateChart.data.labels = stepsFromZero;
  rateChart.data.datasets[0].data = padTo(rates, settings.steps + 1);
  rateChart.update('none');

  // Margin account: red dots are margin calls, the dashed line is the call level
  const balances = [settings.start_margin].concat(rows.map((row) => row.balance));
  const dots = [VIOLET].concat(rows.map((row) => (row.margin_call > 0 ? RED : VIOLET)));
  const level = stepsFromZero.map(() => data.maintenance_margin);
  balanceChart.data.labels = stepsFromZero;
  balanceChart.data.datasets[0].data = padTo(balances, settings.steps + 1);
  balanceChart.data.datasets[0].pointBackgroundColor = dots;
  balanceChart.data.datasets[1].data = level;
  balanceChart.update('none');
}

function rowToHtml(row) {
  const sign = row.change >= 0 ? '+' : '−';
  const cashClass = row.cash >= 0 ? 'pos' : 'neg';
  let balance = money(row.balance);
  if (row.margin_call > 0) {
    balance += ' <span class="call">' + fill(T.call_tag, { amount: money(row.margin_call) }) + '</span>';
  }
  return '<tr>' +
    '<td>' + row.step + '</td>' +
    '<td>' + sign + percent(Math.abs(row.change * 100), 1) + '</td>' +
    '<td>' + signedNumber(row.correlation, 1) + '</td>' +
    '<td>' + percent(row.rate, 2) + '</td>' +
    '<td class="' + cashClass + '">' + signedMoney(row.cash) + '</td>' +
    '<td>' + balance + '</td>' +
    '<td>' + signedMoney(row.interest) + '</td>' +
    '</tr>';
}

function showTable(rows) {
  if (rows.length === 0) {
    $('tb').innerHTML = '<tr><td class="empty" colspan="7">' + T.no_steps + '</td></tr>';
  } else {
    $('tb').innerHTML = rows.map(rowToHtml).join('');
  }
}

function showMonteCarlo(data) {
  const names = { '-1': T.mc_neg, '0': T.mc_zero, '1': T.mc_pos };

  // The longest bar fills half of the track (the other half is for negative values).
  let biggest = 1;
  data.results.forEach((r) => {
    biggest = Math.max(biggest, Math.abs(r.average));
  });

  let html = '<p class="mc-title">' + fill(T.mc_header, { paths: number(data.paths) }) + '</p>';
  data.results.forEach((r) => {
    const width = Math.abs(r.average) / biggest * 50;
    const barClass = r.average >= 0 ? 'pos' : 'neg';
    const value = fill(T.mc_value, {
      average: signedMoney(r.average),
      error: money(2 * r.error),
      points: signedNumber(r.price_gap, 1),
    });
    html += '<div class="mc-row">' +
      '<span class="label">' + names[r.correlation] + '</span>' +
      '<div class="mc-track"><div class="mc-axis"></div>' +
      '<div class="mc-bar ' + barClass + '" style="width:' + width + '%"></div></div>' +
      '<span class="value">' + value + '</span>' +
      '</div>';
  });
  html += '<p class="secondary">' + T.mc_note + '</p>';
  $('mc').innerHTML = html;
}

// ---------------------------------------------------------------------------
// Share link and CSV file
// ---------------------------------------------------------------------------
function round6(x) {
  return Number(x.toFixed(6));
}

// The whole game (settings + moves) written as text, to put in a link.
function encodeGame() {
  const game = {
    s: settings,
    m: moves.map((move) => [round6(move.change), move.correlation, round6(move.noise)]),
  };
  return btoa(JSON.stringify(game));
}

// Read a game from the link (#g=...). Returns null if there is none.
function gameFromLink() {
  const match = location.hash.match(/^#g=(.+)$/);
  if (!match) return null;
  try {
    const game = JSON.parse(atob(match[1]));
    const sharedMoves = game.m.map((m) => ({ change: m[0], correlation: m[1], noise: m[2] }));
    return { settings: game.s, moves: sharedMoves };
  } catch (error) {
    return null;
  }
}

async function clickShare() {
  const url = location.origin + location.pathname + '?lang=' + LANG + '#g=' + encodeGame();
  try {
    await navigator.clipboard.writeText(url);
    showMessage(T.link_copied);
  } catch (error) {
    showMessage(fill(T.link_manual, { url: url }));
  }
}

function clickCsv() {
  if (!lastData || lastData.rows.length === 0) return;
  const lines = ['step,index_change_pct,correlation,rate_pct,cash_flow,margin_balance,margin_call,interest'];
  lastData.rows.forEach((row) => {
    lines.push([
      row.step,
      (row.change * 100).toFixed(2),
      row.correlation,
      row.rate.toFixed(3),
      row.cash.toFixed(2),
      row.balance.toFixed(2),
      row.margin_call.toFixed(2),
      row.interest.toFixed(2),
    ].join(','));
  });
  const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'futures-simulation.csv';
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}

// ---------------------------------------------------------------------------
// Guided tour: a few steps with an explanation and a question each
// ---------------------------------------------------------------------------
// What the tour plays when it reaches each stage (the texts are in T.tour).
const TOUR_ACTIONS = [null, 'up', 'down', 'down', 'up', 'rest'];

// The numbers used in the texts of the tour.
function tourValues() {
  const rows = lastData.rows;
  const last = rows.length > 0 ? rows[rows.length - 1] : null;
  return {
    start_price: number(fixed.start_price),
    point: money(fixed.point_value),
    exposure: money(fixed.start_price * fixed.point_value),
    start: money(settings.start_margin),
    maintenance: money(lastData.maintenance_margin),
    price: last ? number(last.price) : '',
    cash: last ? signedMoney(last.cash) : '',
    balance: last ? money(last.balance) : '',
    call: last ? money(last.margin_call) : '',
    rate: last ? percent(last.rate, 2) : '',
    gap: signedMoney(lastData.summary.gap),
  };
}

function showTourStage(stage) {
  tourStage = stage;
  const content = T.tour[stage];
  const values = tourValues();

  $('tour').hidden = false;
  $('tour-stage').textContent = fill(T.tour_stage, { n: stage + 1, total: T.tour.length });
  $('tour-title').textContent = content.title;
  $('tour-text').textContent = fill(content.text, values);
  $('tour-question').textContent = fill(content.question, values);
  $('tour-feedback').textContent = '';
  $('tour-feedback').className = 'tour-feedback';
  $('tour-next').textContent = stage < T.tour.length - 1 ? T.tour_next : T.tour_finish;

  $('tour-options').innerHTML = '';
  content.options.forEach((text, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = text;
    button.addEventListener('click', () => answerTour(index, button));
    $('tour-options').appendChild(button);
  });
}

function answerTour(index, button) {
  const content = T.tour[tourStage];
  const correct = (index === content.answer);
  const feedback = $('tour-feedback');
  feedback.textContent = fill(correct ? content.right : content.wrong, tourValues());
  feedback.className = 'tour-feedback ' + (correct ? 'right' : 'wrong');
  $('tour-options').querySelectorAll('button').forEach((b) => b.classList.remove('chosen'));
  button.classList.add('chosen');
}

async function startTour() {
  // The tour needs the default settings and a positive correlation.
  applySettings(defaults);
  $('corr').value = '1';
  showCorrelation();
  const ok = await send([]);
  if (ok) showTourStage(0);
}

async function nextTourStage() {
  const stage = tourStage + 1;
  if (stage >= T.tour.length) {
    exitTour();
    return;
  }
  const action = TOUR_ACTIONS[stage];
  let ok = true;
  if (action === 'up') ok = await sendStep(0.02);
  if (action === 'down') ok = await sendStep(-0.02);
  if (action === 'rest') ok = await sendRemainingSteps();
  if (ok) showTourStage(stage);
}

function exitTour() {
  tourStage = -1;
  $('tour').hidden = true;
}

// ---------------------------------------------------------------------------
// Charts
// ---------------------------------------------------------------------------
function chartOptions(tooltipText, tickText) {
  const grid = 'rgba(137,135,129,0.2)';
  const tick = '#898781';
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (item) => tooltipText(item.parsed.y) } },
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: tick } },
      y: { grid: { color: grid }, ticks: { color: tick, callback: tickText } },
    },
  };
}

function buildCharts() {
  flowChart = new Chart($('c-flows'), {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{ data: [], backgroundColor: [], borderRadius: 4, maxBarThickness: 22 }],
    },
    options: chartOptions(signedMoney, number),
  });
  // With no step played yet the bars have no range: give the axis a sensible one.
  flowChart.options.scales.y.suggestedMin = -5000;
  flowChart.options.scales.y.suggestedMax = 5000;

  rateChart = new Chart($('c-rates'), {
    type: 'line',
    data: {
      labels: [],
      datasets: [{ data: [], borderColor: BLUE, backgroundColor: BLUE, borderWidth: 2, pointRadius: 3 }],
    },
    options: chartOptions((v) => percent(v, 2), (v) => percent(v, 1)),
  });

  balanceChart = new Chart($('c-balance'), {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        { data: [], borderColor: VIOLET, backgroundColor: VIOLET, borderWidth: 2, pointRadius: 4, pointBackgroundColor: [] },
        { data: [], borderColor: RED, borderWidth: 1.5, borderDash: [6, 4], pointRadius: 0 },
      ],
    },
    options: chartOptions(money, number),
  });
}

// ---------------------------------------------------------------------------
// Start-up
// ---------------------------------------------------------------------------
function connectButtons() {
  const actions = {
    up: () => clickStep(0.02),
    down: () => clickStep(-0.02),
    random: () => clickStep(null),
    auto: clickPlayToMaturity,
    undo: clickUndo,
    reset: clickRestart,
    share: clickShare,
    csv: clickCsv,
    tour: startTour,
    mc: clickMonteCarlo,
  };
  document.querySelectorAll('[data-action]').forEach((button) => {
    button.addEventListener('click', actions[button.dataset.action]);
  });

  $('corr').addEventListener('input', showCorrelation);
  $('tour-next').addEventListener('click', nextTourStage);
  $('tour-exit').addEventListener('click', exitTour);

  // Changing the language keeps the current game.
  document.querySelectorAll('[data-lang]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (!settings) return;
      event.preventDefault();
      if (link.dataset.lang === LANG) return;   // already in this language
      location.href = '?lang=' + link.dataset.lang + '#g=' + encodeGame();
    });
  });
}

async function start() {
  const response = await fetch('/api/settings');
  const info = await response.json();
  fixed = info.fixed;
  limits = info.limits;
  defaults = info.defaults;

  setupSettings();
  buildCharts();
  connectButtons();

  const shared = gameFromLink();
  if (shared) {
    applySettings(shared.settings);
    if (shared.moves.length > 0) {
      $('corr').value = shared.moves[shared.moves.length - 1].correlation;
    }
    showCorrelation();
    await send(shared.moves);
  } else {
    showCorrelation();
    await send([]);
  }
}

start();
