/** Client for the optional Amadeus proxy API */

const STORAGE_KEY = "us-kr-flights-api-base";

export function getApiBaseUrl() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) return stored.replace(/\/$/, "");

  // Same-origin when API routes are co-deployed (Vercel or local dev)
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host === "localhost" || host.endsWith(".vercel.app")) {
      return window.location.origin.replace(/\/$/, "");
    }
  }
  return "";
}

export function setApiBaseUrl(url) {
  if (!url) {
    localStorage.removeItem(STORAGE_KEY);
    return;
  }
  localStorage.setItem(STORAGE_KEY, url.replace(/\/$/, ""));
}

export async function searchFlights(params, apiBase) {
  const base = (apiBase || getApiBaseUrl()).replace(/\/$/, "");
  if (!base) {
    throw new Error("NO_API");
  }

  const query = new URLSearchParams({
    origin: params.origin,
    destination: params.destination,
    departureDate: params.departure,
    returnDate: params.returnDate,
    adults: String(params.adults || 1),
  });

  const url = `${base}/api/flights?${query}`;
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = body.error || body.message || `Request failed (${response.status})`;
    throw new Error(message);
  }

  return body;
}
