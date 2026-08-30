# US ↔ Korea Flight Prices

A lightweight static web app to search round-trip flight prices between the **United States** and **Korea**. Pick your direction, airports, **departure date**, and **return date**, then view fares or open booking sites with your search pre-filled.

Live demo: enable [GitHub Pages](https://pages.github.com/) in your repo settings (Source: **GitHub Actions**).

## Features

- **Direction toggle**: US → Korea or Korea → US
- **Airport pickers** for major US and Korean hubs (ICN, LAX, JFK, etc.)
- **Departure & return date** inputs with validation
- **Booking site links** (Google Flights, Kayak, Skyscanner) — works on GitHub Pages with no API setup
- **In-app prices** via [Amadeus Flight Offers Search](https://developers.amadeus.com/) when you deploy the included API proxy

## Quick start (GitHub Pages)

1. Push this repo to GitHub.
2. Go to **Settings → Pages → Build and deployment**.
3. Set **Source** to **GitHub Actions**.
4. Merge to `main`; the workflow deploys the `public/` folder automatically.

The site works immediately using external booking links. For prices inside the app, see [API setup](#api-setup-in-app-prices) below.

## Local preview

```bash
npx --yes serve public -p 3000
```

Open http://localhost:3000

## API setup (in-app prices)

Flight APIs cannot be called directly from the browser (CORS + secret keys). This repo includes a small serverless proxy.

### Option A: Vercel (recommended)

1. [Create a free Amadeus developer account](https://developers.amadeus.com/register) and create an app (test keys are fine).
2. Import this repo on [Vercel](https://vercel.com).
3. Add environment variables:
   - `AMADEUS_API_KEY` — your API Key
   - `AMADEUS_API_SECRET` — your API Secret
   - `AMADEUS_ENV` — `test` (default) or `production`
4. Deploy. Open your `*.vercel.app` URL and search — prices load automatically.

You can still host the static UI on GitHub Pages and point it at Vercel:

1. Open the deployed site on GitHub Pages.
2. Click **⚙ Settings**.
3. Set **API base URL** to your Vercel URL (e.g. `https://your-project.vercel.app`).

### Option B: Cloudflare Worker

Deploy `worker/amadeus-proxy.js` as a Worker with secrets `AMADEUS_API_KEY` and `AMADEUS_API_SECRET`, then paste the worker URL in app settings (append `/api/flights` is handled by the worker path).

## Project layout

```
public/           Static site (GitHub Pages)
  index.html
  css/
  js/
api/
  flights.js      Vercel serverless Amadeus proxy
worker/
  amadeus-proxy.js  Optional Cloudflare Worker
.github/workflows/
  deploy-pages.yml
other-assignments/  Coursework (see "Other Assignments" below)
  pandas-fundamentals-go-blue/
  pandas-grouping-hardwood/
  pandas-text-parsing-yost/
  pandas-open-ended-seinfeld/
```

## Notes

- Amadeus **test** data may not include every real-world route or fare; production keys return live offers.
- Return date is required for round-trip search in the UI and API.
- Prices are indicative offers from Amadeus; always confirm on the airline or OTA before booking.

## Other Assignments

This repo also carries coursework that is independent of the flight-price app.

| # | Assignment | Topic | Points |
|---|---|---|---|
| 1 | [🏈 Go Blue: A Pandas Data Exploration](other-assignments/pandas-fundamentals-go-blue/) | pandas fundamentals & Python data manipulation | 100 |
| 2 | [🏀 Hardwood: Grouping, Windows & Reshaping](other-assignments/pandas-grouping-hardwood/) | MultiIndexes, named aggregation, window functions, ranking, streaks | 100 |
| 3 | [🏒 The Yost Feed: Regex, Text & Time](other-assignments/pandas-text-parsing-yost/) | regular expressions, string extraction, clock arithmetic | 100 |
| 4 | [📺 Yada Yada Data: Text, Ambiguity & Defensible Choices](other-assignments/pandas-open-ended-seinfeld/) | regex on prose, and five questions with no right answer | 100 |

Each assignment is a self-contained folder: a Jupyter notebook with ten
questions, a dataset, public asserts that students run themselves, hidden
asserts that carry the grade, and an autograder. See
[`other-assignments/`](other-assignments/) for how they are structured and how
to grade them.

## License

MIT
