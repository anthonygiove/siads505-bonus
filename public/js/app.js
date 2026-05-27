import {
  US_AIRPORTS,
  KOREA_AIRPORTS,
  formatAirportOption,
  findAirport,
} from "./airports.js";
import { buildExternalLinks } from "./links.js";
import { searchFlights, getApiBaseUrl, setApiBaseUrl } from "./api.js";

const $ = (id) => document.getElementById(id);

const originSelect = $("origin-airport");
const destinationSelect = $("destination-airport");
const departureInput = $("departure-date");
const returnInput = $("return-date");
const adultsInput = $("adults");
const searchBtn = $("search-btn");
const statusEl = $("status");
const resultsSection = $("results-section");
const resultsList = $("results-list");
const resultsTitle = $("results-title");
const resultsMeta = $("results-meta");
const externalLinksSection = $("external-links");
const linkButtons = $("link-buttons");
const settingsDialog = $("settings-dialog");
const settingsForm = $("settings-form");
const apiBaseInput = $("api-base-url");

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function addDays(iso, days) {
  const d = new Date(iso + "T12:00:00");
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function getDirection() {
  return document.querySelector('input[name="direction"]:checked')?.value || "us-to-kr";
}

function populateSelect(select, airports, selectedCode) {
  select.innerHTML = "";
  for (const airport of airports) {
    const opt = document.createElement("option");
    opt.value = airport.code;
    opt.textContent = formatAirportOption(airport);
    if (airport.code === selectedCode) opt.selected = true;
    select.appendChild(opt);
  }
}

function syncAirportsForDirection() {
  const direction = getDirection();
  const prevOrigin = originSelect.value;
  const prevDest = destinationSelect.value;

  if (direction === "us-to-kr") {
    populateSelect(originSelect, US_AIRPORTS, US_AIRPORTS.some((a) => a.code === prevOrigin) ? prevOrigin : "LAX");
    populateSelect(
      destinationSelect,
      KOREA_AIRPORTS,
      KOREA_AIRPORTS.some((a) => a.code === prevDest) ? prevDest : "ICN"
    );
  } else {
    populateSelect(originSelect, KOREA_AIRPORTS, KOREA_AIRPORTS.some((a) => a.code === prevOrigin) ? prevOrigin : "ICN");
    populateSelect(
      destinationSelect,
      US_AIRPORTS,
      US_AIRPORTS.some((a) => a.code === prevDest) ? prevDest : "LAX"
    );
  }
}

function setDefaultDates() {
  const today = todayISO();
  departureInput.min = today;
  returnInput.min = today;

  if (!departureInput.value) {
    departureInput.value = addDays(today, 30);
  }
  if (!returnInput.value) {
    returnInput.value = addDays(departureInput.value, 14);
  }
}

function showStatus(message, type = "info") {
  statusEl.hidden = false;
  statusEl.textContent = message;
  statusEl.className = `status status--${type}`;
}

function hideStatus() {
  statusEl.hidden = true;
}

function getSearchParams() {
  return {
    origin: originSelect.value,
    destination: destinationSelect.value,
    departure: departureInput.value,
    returnDate: returnInput.value,
    adults: parseInt(adultsInput.value, 10) || 1,
    direction: getDirection(),
  };
}

function validateSearch(params) {
  if (!params.departure || !params.returnDate) {
    return "Please select departure and return dates.";
  }
  if (params.returnDate < params.departure) {
    return "Return date must be on or after the departure date.";
  }
  if (params.origin === params.destination) {
    return "Origin and destination must be different.";
  }
  return null;
}

function renderExternalLinks(params) {
  const links = buildExternalLinks(params);
  linkButtons.innerHTML = links
    .map(
      (l) =>
        `<a href="${l.url}" target="_blank" rel="noopener noreferrer">${l.icon} ${l.label}</a>`
    )
    .join("");
  externalLinksSection.hidden = false;
}

function formatTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDuration(isoDuration) {
  if (!isoDuration) return "";
  const match = isoDuration.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
  if (!match) return isoDuration;
  const h = match[1] ? `${match[1]}h` : "";
  const m = match[2] ? ` ${match[2]}m` : "";
  return `${h}${m}`.trim();
}

function countStops(itinerary) {
  const segments = itinerary?.segments || [];
  return Math.max(0, segments.length - 1);
}

function renderFlightOffers(offers, params) {
  resultsSection.hidden = false;
  resultsTitle.textContent = "Flight offers";

  const originLabel = findAirport(params.origin, [...US_AIRPORTS, ...KOREA_AIRPORTS]);
  const destLabel = findAirport(params.destination, [...US_AIRPORTS, ...KOREA_AIRPORTS]);
  resultsMeta.textContent = `${originLabel?.city || params.origin} → ${destLabel?.city || params.destination} · ${params.departure} – ${params.returnDate}`;

  if (!offers?.length) {
    resultsList.innerHTML =
      '<li class="status status--warn" style="list-style:none">No offers found for these dates. Try different dates or use the booking links below.</li>';
    return;
  }

  resultsList.innerHTML = offers
    .map((offer) => {
      const out = offer.itineraries?.[0];
      const back = offer.itineraries?.[1];
      const price = offer.price;
      const currency = price?.currency || "USD";
      const total = price?.total ?? price?.grandTotal ?? "—";
      const stopsOut = countStops(out);
      const stopsBack = back ? countStops(back) : 0;
      const airline =
        out?.segments?.[0]?.carrierCode ||
        offer.validatingAirlineCodes?.join(", ") ||
        "—";

      const outFrom = out?.segments?.[0]?.departure?.iataCode;
      const outTo = out?.segments?.at(-1)?.arrival?.iataCode;
      const outDep = out?.segments?.[0]?.departure?.at;
      const outArr = out?.segments?.at(-1)?.arrival?.at;

      const backFrom = back?.segments?.[0]?.departure?.iataCode;
      const backTo = back?.segments?.at(-1)?.arrival?.iataCode;
      const backDep = back?.segments?.[0]?.departure?.at;
      const backArr = back?.segments?.at(-1)?.arrival?.at;

      return `
        <li class="flight-card">
          <div class="flight-card__price">
            ${currency} ${total}
            <small>round trip</small>
          </div>
          <div class="flight-card__route">
            <div class="flight-card__leg">
              <span class="flight-card__airports">${outFrom} → ${outTo}</span>
              <span class="flight-card__times">${formatTime(outDep)} – ${formatTime(outArr)}</span>
            </div>
            ${
              back
                ? `<div class="flight-card__leg">
              <span class="flight-card__airports">${backFrom} → ${backTo}</span>
              <span class="flight-card__times">${formatTime(backDep)} – ${formatTime(backArr)}</span>
            </div>`
                : ""
            }
          </div>
          <div class="flight-card__meta">
            <span class="flight-card__airline">${airline}</span>
            <span class="flight-card__stops ${stopsOut === 0 && stopsBack === 0 ? "flight-card__stops--direct" : ""}">
              Out: ${stopsOut === 0 ? "Direct" : `${stopsOut} stop${stopsOut > 1 ? "s" : ""}`}
              ${back ? ` · Back: ${stopsBack === 0 ? "Direct" : `${stopsBack} stop${stopsBack > 1 ? "s" : ""}`}` : ""}
            </span>
            <span>${formatDuration(out?.duration)}${back ? ` / ${formatDuration(back?.duration)}` : ""}</span>
          </div>
        </li>
      `;
    })
    .join("");
}

async function runSearch() {
  const params = getSearchParams();
  const error = validateSearch(params);
  if (error) {
    showStatus(error, "error");
    return;
  }

  hideStatus();
  resultsSection.hidden = true;
  renderExternalLinks(params);

  searchBtn.disabled = true;
  showStatus("Searching…", "info");

  const apiBase = getApiBaseUrl();

  try {
    const data = await searchFlights(params, apiBase);
    hideStatus();
    renderFlightOffers(data.offers || data.data || [], params);
    if ((data.offers || data.data || []).length > 0) {
      showStatus(`Found ${(data.offers || data.data).length} offer(s) via Amadeus.`, "info");
    }
  } catch (err) {
    if (err.message === "NO_API") {
      hideStatus();
      showStatus(
        "Showing booking site links. For in-app prices, deploy the API (see Settings ⚙) or host on Vercel with Amadeus keys.",
        "warn"
      );
    } else {
      showStatus(`API: ${err.message}. Use the booking links below for live fares.`, "warn");
    }
  } finally {
    searchBtn.disabled = false;
  }
}

function swapAirports() {
  const o = originSelect.value;
  const d = destinationSelect.value;
  originSelect.value = d;
  destinationSelect.value = o;

  const direction = getDirection();
  const originInUS = US_AIRPORTS.some((a) => a.code === originSelect.value);
  const destInKR = KOREA_AIRPORTS.some((a) => a.code === destinationSelect.value);

  if (direction === "us-to-kr" && !(originInUS && destInKR)) {
    document.querySelector('input[name="direction"][value="kr-to-us"]').checked = true;
    syncAirportsForDirection();
    originSelect.value = d;
    destinationSelect.value = o;
  } else if (direction === "kr-to-us") {
    const originInKR = KOREA_AIRPORTS.some((a) => a.code === originSelect.value);
    const destInUS = US_AIRPORTS.some((a) => a.code === destinationSelect.value);
    if (!(originInKR && destInUS)) {
      document.querySelector('input[name="direction"][value="us-to-kr"]').checked = true;
      syncAirportsForDirection();
      originSelect.value = d;
      destinationSelect.value = o;
    }
  }
}

function initSettings() {
  apiBaseInput.value = getApiBaseUrl();

  $("settings-toggle").addEventListener("click", () => {
    apiBaseInput.value = getApiBaseUrl();
    settingsDialog.showModal();
  });

  $("settings-clear").addEventListener("click", () => {
    apiBaseInput.value = "";
    setApiBaseUrl("");
  });

  settingsForm.addEventListener("submit", (e) => {
    e.preventDefault();
    setApiBaseUrl(apiBaseInput.value.trim());
    settingsDialog.close();
    showStatus("API settings saved.", "info");
  });
}

function init() {
  document.querySelectorAll('input[name="direction"]').forEach((radio) => {
    radio.addEventListener("change", syncAirportsForDirection);
  });

  departureInput.addEventListener("change", () => {
    returnInput.min = departureInput.value;
    if (returnInput.value < departureInput.value) {
      returnInput.value = addDays(departureInput.value, 7);
    }
  });

  searchBtn.addEventListener("click", runSearch);
  $("swap-airports").addEventListener("click", swapAirports);

  initSettings();
  syncAirportsForDirection();
  setDefaultDates();

  // Initial search shows external links for default route
  runSearch();
}

init();
