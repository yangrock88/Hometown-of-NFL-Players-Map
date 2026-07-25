#!/usr/bin/env python3
"""Refresh the map's data from live NFL sources.

Usage:
    python update_data.py

Pulls current rosters, draft history, depth charts (starter status),
OverTheCap salaries and ESPN birthplaces, geocodes each hometown, and writes
assets/data.js (which the map loads directly). Safe to run as often as you
like -- results are cached under data/cache to stay fast and polite.

No external packages required: standard library only.
"""
from etl.build import main

if __name__ == "__main__":
    main()
