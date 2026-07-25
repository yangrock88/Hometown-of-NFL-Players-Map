"""Turn 'City, ST' birthplaces into lat/lng.

Strategy (fast + polite):
  1. An offline US-cities table (~30k rows) resolves the vast majority instantly.
  2. Anything missed falls back to OSM Nominatim (1 req/sec) and is cached.
  3. Unresolved places fall back to a state centroid so the point still lands
     somewhere sensible.
"""
import time
import urllib.parse

from . import config, fetch

_CACHE_NAME = "geocode.json"

# Rough geographic centroids for US states / DC — a graceful last resort.
STATE_CENTROIDS = {
    "AL": (32.8, -86.8), "AK": (64.2, -149.5), "AZ": (34.2, -111.7),
    "AR": (34.9, -92.4), "CA": (37.2, -119.3), "CO": (39.0, -105.5),
    "CT": (41.6, -72.7), "DE": (39.0, -75.5), "DC": (38.9, -77.0),
    "FL": (28.6, -82.4), "GA": (32.6, -83.4), "HI": (20.3, -156.4),
    "ID": (44.4, -114.6), "IL": (40.0, -89.2), "IN": (39.9, -86.3),
    "IA": (42.0, -93.5), "KS": (38.5, -98.4), "KY": (37.5, -85.3),
    "LA": (31.0, -92.0), "ME": (45.4, -69.2), "MD": (39.0, -76.8),
    "MA": (42.3, -71.8), "MI": (44.3, -85.4), "MN": (46.3, -94.3),
    "MS": (32.7, -89.7), "MO": (38.4, -92.5), "MT": (47.0, -109.6),
    "NE": (41.5, -99.8), "NV": (39.3, -116.6), "NH": (43.7, -71.6),
    "NJ": (40.1, -74.7), "NM": (34.4, -106.1), "NY": (42.9, -75.6),
    "NC": (35.5, -79.4), "ND": (47.5, -100.3), "OH": (40.3, -82.8),
    "OK": (35.6, -97.5), "OR": (44.0, -120.5), "PA": (40.9, -77.8),
    "RI": (41.7, -71.6), "SC": (33.9, -80.9), "SD": (44.4, -100.2),
    "TN": (35.9, -86.4), "TX": (31.5, -99.3), "UT": (39.3, -111.7),
    "VT": (44.1, -72.7), "VA": (37.5, -78.9), "WA": (47.4, -120.5),
    "WV": (38.6, -80.6), "WI": (44.6, -89.9), "WY": (43.0, -107.6),
}


def _key(city, state):
    return f"{(city or '').strip().lower()}|{(state or '').strip().upper()}"


class Geocoder:
    def __init__(self):
        self.cache = fetch.load_json_cache(_CACHE_NAME)
        self._offline = None
        self._dirty = False
        self._last_osm = 0.0

    def _load_offline(self):
        if self._offline is not None:
            return
        self._offline = {}
        try:
            rows = fetch.download_csv(
                config.US_CITIES_CSV, cache_name="us_cities.csv", max_age_h=720)
        except Exception:
            rows = []
        for r in rows:
            city = r.get("CITY") or r.get("city")
            st = r.get("STATE_CODE") or r.get("state_code")
            lat = r.get("LATITUDE") or r.get("latitude")
            lng = r.get("LONGITUDE") or r.get("longitude")
            if not (city and st and lat and lng):
                continue
            k = _key(city, st)
            # keep first (dataset is largest-first-ish); don't clobber
            self._offline.setdefault(k, (float(lat), float(lng)))

    def geocode(self, city, state, country="USA"):
        """Return (lat, lng, precision) or None. precision in city|osm|state."""
        if not state and not city:
            return None
        k = _key(city, state)
        if k in self.cache:
            v = self.cache[k]
            return (v[0], v[1], v[2]) if v else None

        self._load_offline()
        hit = self._offline.get(k)
        if hit:
            return self._store(k, hit[0], hit[1], "city")

        # International or missing-from-table -> OSM (only for USA/CAN-ish keeps sane)
        osm = self._nominatim(city, state, country)
        if osm:
            return self._store(k, osm[0], osm[1], "osm")

        cent = STATE_CENTROIDS.get((state or "").upper())
        if cent:
            return self._store(k, cent[0], cent[1], "state")

        self._store(k, None, None, None, empty=True)
        return None

    def _nominatim(self, city, state, country):
        q = ", ".join([p for p in (city, state, country) if p])
        if not q:
            return None
        # polite 1.1s spacing
        wait = 1.1 - (time.time() - self._last_osm)
        if wait > 0:
            time.sleep(wait)
        self._last_osm = time.time()
        try:
            url = config.NOMINATIM + "?" + urllib.parse.urlencode(
                {"q": q, "format": "json", "limit": 1})
            data = fetch.get_json(url, timeout=20, retries=2)
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            return None
        return None

    def _store(self, k, lat, lng, prec, empty=False):
        self.cache[k] = None if empty else [lat, lng, prec]
        self._dirty = True
        return None if empty else (lat, lng, prec)

    def flush(self):
        if self._dirty:
            fetch.save_json_cache(_CACHE_NAME, self.cache)
            self._dirty = False
