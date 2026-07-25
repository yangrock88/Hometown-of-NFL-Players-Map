# Hometown of NFL Players — Interactive Map

An interactive map of where **every current NFL player** (all 32 teams) grew up.
Each player is a marker placed at their hometown and colored by team. Click a
marker to open a full profile — position, physicals, college, draft slot,
depth-chart role, and contract value.

**Live map:** open `index.html` locally, or publish the repo with GitHub Pages.

![preview](docs/preview.png)

---

## Design thinking

The map was shaped around a few real user questions ("jobs to be done"):

| Question a fan/scout asks | How the map answers it |
|---|---|
| *Where does the talent come from?* | One dot per player at their hometown, jittered so shared cities fan out. |
| *Who are the difference-makers?* | Projected **starters** render larger; **1st-round picks** show as stars. |
| *Which players matter to my team?* | Markers are **team-colored**; filter to one or many teams. |
| *Who's the local kid?* | Filter by **home state**. |
| *Where's the money?* | "Top performers by salary (APY)" slider + salary on every profile. |
| *Slice any way I want* | Combine filters: conference, draft round, position group, starters. |

Visual language: a dark neon analytics palette (navy canvas; magenta / purple /
cyan / amber accents) over a CARTO dark-matter basemap, so bright team colors
and stars pop without competing with map labels.

---

## Data sources

All data is public and refreshed by `update_data.py`:

- **[nflverse](https://github.com/nflverse/nflverse)** — current rosters, positions,
  headshots, draft history, depth charts (starter status), and OverTheCap contracts.
- **ESPN athlete API** — player birthplaces (hometowns).
- **OpenStreetMap / offline US-cities table** — geocoding hometown → lat/lng.

Joins are keyed on stable ids (`gsis_id`, `espn_id`, `otc_id`).

---

## Refreshing the data (dynamic + updatable)

The dataset is decoupled from the app. Regenerate any time:

```bash
python update_data.py
```

This writes `assets/data.js` (and `data/players.json`). No third-party Python
packages are required — standard library only. Results are cached under
`data/cache/` so re-runs are fast and gentle on upstream servers.

To roll to a new season, change `SEASON` in `etl/config.py` and re-run.

### Automated cadence

`.github/workflows/refresh-data.yml` runs the refresh on a schedule (weekly by
default — edit the `cron` to taste) and commits the updated data, so the
published map stays current with zero manual effort.

---

## Project layout

```
index.html            # the map (loads assets/data.js)
assets/
  app.js              # map, markers, filters, profile panel
  styles.css          # dark-neon theme
  data.js             # generated dataset (window.NFL_DATA)
etl/
  config.py           # feeds + season knob
  fetch.py            # cached HTTP + CSV helpers
  teams.py            # team colors / divisions
  espn.py             # birthplace lookups (threaded, cached)
  geocode.py          # offline + Nominatim geocoding
  build.py            # orchestration -> data.js
update_data.py        # entry point
```

---

*Built and maintained by Rocky Yang.*
