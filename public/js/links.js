/** Build deep links to external flight search engines */

export function buildGoogleFlightsUrl({ origin, destination, departure, returnDate, adults }) {
  const q = [
    "Flights",
    `from ${origin}`,
    `to ${destination}`,
    `on ${departure}`,
    returnDate ? `through ${returnDate}` : "",
    adults > 1 ? `${adults} adults` : "",
  ]
    .filter(Boolean)
    .join(" ");

  return `https://www.google.com/travel/flights?q=${encodeURIComponent(q)}`;
}

export function buildKayakUrl({ origin, destination, departure, returnDate }) {
  const params = new URLSearchParams({
    sort: "bestflight_a",
    fs: `stops=0;airports=-${origin},-${destination}`,
  });
  return `https://www.kayak.com/flights/${origin}-${destination}/${departure}/${returnDate}?${params}`;
}

export function buildSkyscannerUrl({ origin, destination, departure, returnDate }) {
  const dep = departure.replace(/-/g, "");
  const ret = returnDate.replace(/-/g, "");
  return `https://www.skyscanner.com/transport/flights/${origin.toLowerCase()}/${destination.toLowerCase()}/${dep}/${ret}/`;
}

export function buildExternalLinks(search) {
  return [
    {
      label: "Google Flights",
      url: buildGoogleFlightsUrl(search),
      icon: "✈",
    },
    {
      label: "Kayak",
      url: buildKayakUrl(search),
      icon: "🛫",
    },
    {
      label: "Skyscanner",
      url: buildSkyscannerUrl(search),
      icon: "🔍",
    },
  ];
}
