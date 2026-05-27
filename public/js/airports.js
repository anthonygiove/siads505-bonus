/** Major airports for US ↔ Korea routes */

export const US_AIRPORTS = [
  { code: "JFK", city: "New York", name: "John F. Kennedy" },
  { code: "EWR", city: "New York", name: "Newark Liberty" },
  { code: "LGA", city: "New York", name: "LaGuardia" },
  { code: "LAX", city: "Los Angeles", name: "Los Angeles Intl" },
  { code: "SFO", city: "San Francisco", name: "San Francisco Intl" },
  { code: "SEA", city: "Seattle", name: "Seattle-Tacoma" },
  { code: "ORD", city: "Chicago", name: "O'Hare" },
  { code: "ATL", city: "Atlanta", name: "Hartsfield-Jackson" },
  { code: "DFW", city: "Dallas", name: "Dallas/Fort Worth" },
  { code: "BOS", city: "Boston", name: "Logan" },
  { code: "IAD", city: "Washington DC", name: "Dulles" },
  { code: "DCA", city: "Washington DC", name: "Reagan National" },
  { code: "HNL", city: "Honolulu", name: "Daniel K. Inouye" },
  { code: "LAS", city: "Las Vegas", name: "Harry Reid" },
  { code: "DEN", city: "Denver", name: "Denver Intl" },
];

export const KOREA_AIRPORTS = [
  { code: "ICN", city: "Seoul", name: "Incheon Intl" },
  { code: "GMP", city: "Seoul", name: "Gimpo" },
  { code: "PUS", city: "Busan", name: "Gimhae Intl" },
  { code: "CJU", city: "Jeju", name: "Jeju Intl" },
];

export function formatAirportOption(airport) {
  return `${airport.code} — ${airport.city} (${airport.name})`;
}

export function findAirport(code, list) {
  return list.find((a) => a.code === code);
}
