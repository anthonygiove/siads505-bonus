/**
 * Optional Cloudflare Worker proxy for GitHub Pages deployments.
 * Deploy separately and set the worker URL in the app settings.
 *
 * Secrets: AMADEUS_API_KEY, AMADEUS_API_SECRET
 * Optional var: AMADEUS_ENV = "production" | "test" (default test)
 */

const AMADEUS_HOSTS = {
  test: "https://test.api.amadeus.com",
  production: "https://api.amadeus.com",
};

let cachedToken = null;
let tokenExpiresAt = 0;

async function getToken(env) {
  const now = Date.now();
  if (cachedToken && now < tokenExpiresAt - 60_000) return cachedToken;

  const host = AMADEUS_HOSTS[env.AMADEUS_ENV === "production" ? "production" : "test"];
  const body = new URLSearchParams({
    grant_type: "client_credentials",
    client_id: env.AMADEUS_API_KEY,
    client_secret: env.AMADEUS_API_SECRET,
  });

  const res = await fetch(`${host}/v1/security/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error_description || "Auth failed");

  cachedToken = data.access_token;
  tokenExpiresAt = now + (data.expires_in || 1800) * 1000;
  return { token: cachedToken, host };
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept",
  };
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    const url = new URL(request.url);
    if (!url.pathname.endsWith("/api/flights")) {
      return new Response("US-Korea Flights API proxy", { headers: corsHeaders() });
    }

    const origin = url.searchParams.get("origin");
    const destination = url.searchParams.get("destination");
    const departureDate = url.searchParams.get("departureDate");
    const returnDate = url.searchParams.get("returnDate");
    const adults = url.searchParams.get("adults") || "1";

    if (!origin || !destination || !departureDate) {
      return Response.json(
        { error: "origin, destination, departureDate required" },
        { status: 400, headers: corsHeaders() }
      );
    }

    try {
      const { token, host } = await getToken(env);
      const params = new URLSearchParams({
        originLocationCode: origin.toUpperCase(),
        destinationLocationCode: destination.toUpperCase(),
        departureDate,
        adults,
        currencyCode: "USD",
        max: "15",
      });
      if (returnDate) params.set("returnDate", returnDate);

      const searchRes = await fetch(`${host}/v2/shopping/flight-offers?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const payload = await searchRes.json();

      if (!searchRes.ok) {
        const err =
          payload.errors?.map((e) => e.detail).join("; ") || "Search failed";
        return Response.json({ error: err }, { status: searchRes.status, headers: corsHeaders() });
      }

      return Response.json({ offers: payload.data || [] }, { headers: corsHeaders() });
    } catch (e) {
      return Response.json({ error: e.message }, { status: 500, headers: corsHeaders() });
    }
  },
};
