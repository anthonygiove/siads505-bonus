/**
 * Vercel serverless proxy for Amadeus Flight Offers Search.
 * Set AMADEUS_API_KEY and AMADEUS_API_SECRET in your deployment environment.
 */

const AMADEUS_HOST =
  process.env.AMADEUS_ENV === "production"
    ? "https://api.amadeus.com"
    : "https://test.api.amadeus.com";

let cachedToken = null;
let tokenExpiresAt = 0;

async function getAccessToken() {
  const now = Date.now();
  if (cachedToken && now < tokenExpiresAt - 60_000) {
    return cachedToken;
  }

  const clientId = process.env.AMADEUS_API_KEY;
  const clientSecret = process.env.AMADEUS_API_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error("Amadeus API credentials are not configured on the server.");
  }

  const body = new URLSearchParams({
    grant_type: "client_credentials",
    client_id: clientId,
    client_secret: clientSecret,
  });

  const res = await fetch(`${AMADEUS_HOST}/v1/security/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error_description || data.error || "Failed to authenticate with Amadeus");
  }

  cachedToken = data.access_token;
  tokenExpiresAt = now + (data.expires_in || 1800) * 1000;
  return cachedToken;
}

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
}

function validateDate(iso) {
  return /^\d{4}-\d{2}-\d{2}$/.test(iso);
}

export default async function handler(req, res) {
  setCors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { origin, destination, departureDate, returnDate, adults } = req.query;

  if (!origin || !destination || !departureDate) {
    return res.status(400).json({
      error: "Missing required query params: origin, destination, departureDate",
    });
  }

  if (!validateDate(departureDate) || (returnDate && !validateDate(returnDate))) {
    return res.status(400).json({ error: "Dates must be YYYY-MM-DD" });
  }

  const adultCount = Math.min(9, Math.max(1, parseInt(adults, 10) || 1));

  try {
    const token = await getAccessToken();
    const params = new URLSearchParams({
      originLocationCode: String(origin).toUpperCase(),
      destinationLocationCode: String(destination).toUpperCase(),
      departureDate,
      adults: String(adultCount),
      currencyCode: "USD",
      max: "15",
      nonStop: "false",
    });

    if (returnDate) {
      params.set("returnDate", returnDate);
    }

    const searchRes = await fetch(
      `${AMADEUS_HOST}/v2/shopping/flight-offers?${params}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    const payload = await searchRes.json();

    if (!searchRes.ok) {
      const detail =
        payload.errors?.map((e) => e.detail || e.title).join("; ") ||
        payload.error_description ||
        "Flight search failed";
      return res.status(searchRes.status).json({ error: detail });
    }

    return res.status(200).json({
      offers: payload.data || [],
      meta: payload.meta,
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message || "Internal server error" });
  }
}
