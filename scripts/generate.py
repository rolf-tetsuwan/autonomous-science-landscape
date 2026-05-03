#!/usr/bin/env python3
"""
Generate all views from data/*.yaml.

Outputs (all at repo root):
    index.html         sortable + filterable table with logos
    README.md          framework + tag legend
    companies.md       master table
    by-category.md     companies grouped by category
    by-thesis.md       companies grouped by thesis
    theses.md          full thesis writeups
    companies.csv      machine-readable

Usage:
    python3 scripts/generate.py
    python3 scripts/generate.py --fetch-logos     # also download missing logos
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LOGOS = ROOT / "logos"

BANNER_HTML = "<!-- GENERATED — edit data/*.yaml and run scripts/generate.py -->"
BANNER_MD = "<!-- GENERATED — edit data/*.yaml and run `python3 scripts/generate.py` -->"


# ---------------------------------------------------------------------------
# data load + validation
# ---------------------------------------------------------------------------

def load_data():
    with open(DATA / "categories.yaml") as f:
        categories = yaml.safe_load(f)
    with open(DATA / "theses.yaml") as f:
        theses = yaml.safe_load(f)
    with open(DATA / "companies.yaml") as f:
        companies = yaml.safe_load(f)
    return categories, theses, companies


# ---------------------------------------------------------------------------
# tag schema helpers
#
# A tag is either a plain string key (legacy) OR a dict {k, m, i} where
#   k = category/thesis key
#   m = marketing emphasis 0-5 (how loud the company is in their pitch)
#   i = influence/maturity 0-5 (actual track record / install base / revenue)
# ---------------------------------------------------------------------------

def tag_key(item) -> str:
    if isinstance(item, str):
        return item
    return item["k"]


def tag_m(item) -> int | None:
    if isinstance(item, dict):
        return item.get("m")
    return None


def tag_i(item) -> int | None:
    if isinstance(item, dict):
        return item.get("i")
    return None


def tag_score(item) -> tuple[int | None, int | None]:
    return tag_m(item), tag_i(item)


VALID_AI_LEVELS = {"ai-native", "ai-adopting", "ai-adjacent", "standard-oss"}
VALID_MATURITIES = {"public", "late-stage", "mid-stage", "early", "stealth", "mature-private", "standard"}
VALID_PRICINGS = {"premium", "mid", "economical", "free"}
VALID_STATUSES = {"active", "acquired", "defunct", "dormant"}


def validate(categories, theses, companies) -> None:
    cat_keys = {c["key"] for c in categories}
    thesis_keys = {t["key"] for t in theses}
    errors: list[str] = []
    warnings: list[str] = []
    for c in companies:
        for item in c.get("categories") or []:
            k = tag_key(item)
            if k not in cat_keys:
                errors.append(f"{c['name']}: unknown category '{k}'")
            m, i = tag_score(item)
            if m is not None and not (0 <= m <= 5):
                errors.append(f"{c['name']}: category {k} marketing score {m} out of [0,5]")
            if i is not None and not (0 <= i <= 5):
                errors.append(f"{c['name']}: category {k} influence score {i} out of [0,5]")
            if isinstance(item, dict) and (m is None or i is None):
                warnings.append(f"{c['name']}: category {k} missing m or i score")
        for item in c.get("theses") or []:
            k = tag_key(item)
            if k not in thesis_keys:
                errors.append(f"{c['name']}: unknown thesis '{k}'")
            m, i = tag_score(item)
            if m is not None and not (0 <= m <= 5):
                errors.append(f"{c['name']}: thesis {k} marketing score {m} out of [0,5]")
            if i is not None and not (0 <= i <= 5):
                errors.append(f"{c['name']}: thesis {k} influence score {i} out of [0,5]")
            if isinstance(item, dict) and (m is None or i is None):
                warnings.append(f"{c['name']}: thesis {k} missing m or i score")
        s = c.get("status") or "active"
        if s not in VALID_STATUSES:
            errors.append(f"{c['name']}: invalid status '{s}' (must be one of {VALID_STATUSES})")
        a = c.get("ai_level")
        if a and a not in VALID_AI_LEVELS:
            errors.append(f"{c['name']}: invalid ai_level '{a}'")
        m_ = c.get("maturity")
        if m_ and m_ not in VALID_MATURITIES:
            errors.append(f"{c['name']}: invalid maturity '{m_}'")
        p = c.get("pricing")
        if p and p not in VALID_PRICINGS:
            errors.append(f"{c['name']}: invalid pricing '{p}'")
    if warnings:
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# logos
# ---------------------------------------------------------------------------

_GOOGLE_GENERIC_SIZE = 726  # Google sz=128 returns this exact byte length when no favicon found


def _try_fetch(url: str, min_bytes: int = 500, reject_size: int | None = None) -> bytes | None:
    """Fetch URL; return body if >= min_bytes (and not exactly reject_size)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        if len(data) < min_bytes:
            return None
        if reject_size is not None and len(data) == reject_size:
            return None
        return data
    except Exception:  # noqa: BLE001
        return None


def _scrape_homepage_icon(domain: str) -> str | None:
    """Fetch homepage HTML and extract first usable icon URL from <link rel='...icon...'>."""
    import re
    from urllib.parse import urljoin
    for base in (f"https://{domain}/", f"https://www.{domain}/"):
        try:
            req = urllib.request.Request(base, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read(200_000).decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        # Look for icon-type link tags. Prefer apple-touch-icon (largest) > icon > shortcut icon.
        patterns = [
            r'<link[^>]+rel=["\']?apple-touch-icon[^"\']*["\']?[^>]*href=["\']([^"\']+)["\']',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']?apple-touch-icon[^"\']*["\']?',
            r'<link[^>]+rel=["\']?icon["\']?[^>]*href=["\']([^"\']+)["\']',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']?icon["\']?',
            r'<link[^>]+rel=["\']?shortcut icon["\']?[^>]*href=["\']([^"\']+)["\']',
        ]
        for pat in patterns:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                return urljoin(base, m.group(1))
    return None


def fetch_logos(companies, force: bool = False) -> None:
    """Fetch logos with cascading fallbacks.

    Order: DuckDuckGo → Google sz=128 (rejecting generic) → direct apple-touch / favicon paths
        → homepage HTML scrape for <link rel="icon">.
    """
    LOGOS.mkdir(exist_ok=True)
    fetched = skipped = failed = 0
    for c in companies:
        domain = c.get("domain")
        slug = c["slug"]
        out = LOGOS / f"{slug}.png"
        if not domain:
            skipped += 1
            continue
        if out.exists() and not force:
            skipped += 1
            continue

        sources: list[tuple[str, int | None]] = [
            (f"https://icons.duckduckgo.com/ip3/{domain}.ico", None),
            (f"https://icons.duckduckgo.com/ip3/www.{domain}.ico", None),
            (f"https://www.google.com/s2/favicons?domain={domain}&sz=128", _GOOGLE_GENERIC_SIZE),
            (f"https://{domain}/apple-touch-icon.png", None),
            (f"https://{domain}/apple-touch-icon-precomposed.png", None),
            (f"https://www.{domain}/apple-touch-icon.png", None),
            (f"https://{domain}/favicon.png", None),
            (f"https://{domain}/favicon.ico", None),
        ]

        data = None
        chosen = None
        for url, reject in sources:
            data = _try_fetch(url, min_bytes=500, reject_size=reject)
            if data:
                chosen = url
                break

        # Last resort: scrape homepage for icon URL
        if not data:
            scraped = _scrape_homepage_icon(domain)
            if scraped:
                data = _try_fetch(scraped, min_bytes=200)
                if data:
                    chosen = scraped

        if data:
            out.write_bytes(data)
            fetched += 1
            short = chosen.split("/")[2] if chosen else "?"
            print(f"  {slug}.png ← {short} ({len(data)}B)")
        else:
            print(f"  {slug}: FAILED on all sources for {domain}", file=sys.stderr)
            failed += 1
    print(f"logos: {fetched} fetched, {skipped} skipped, {failed} failed")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _index(items, key="key"):
    return {i[key]: i for i in items}


def _company_count_by(companies, field):
    """Count companies that have a given key in a list-typed field (handles scored tags)."""
    counter: Counter = Counter()
    for c in companies:
        for item in c.get(field) or []:
            counter[tag_key(item)] += 1
    return counter


def _score_sums_by(companies, field):
    """Sum marketing and influence scores per tag key. Returns dict[key] = {'m': int, 'i': int, 'n': int}."""
    out: dict[str, dict[str, int]] = defaultdict(lambda: {"m": 0, "i": 0, "n": 0})
    for c in companies:
        for item in c.get(field) or []:
            k = tag_key(item)
            m = tag_m(item) or 0
            i = tag_i(item) or 0
            out[k]["m"] += m
            out[k]["i"] += i
            out[k]["n"] += 1
    return dict(out)


def _md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ")


def _yes(v) -> bool:
    return bool(v)


# ---------------------------------------------------------------------------
# index.html
# ---------------------------------------------------------------------------

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Autonomous Science Landscape</title>
__BANNER__
<style>
  :root {
    --bg: #fafafa;
    --fg: #1f2024;
    --muted: #6b7280;
    --line: #e5e7eb;
    --line-strong: #d1d5db;
    --accent: #1849a9;
    --row-hover: #f3f4f6;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--fg);
    font: 14px/1.45 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
  }
  header {
    padding: 20px 24px 12px;
    border-bottom: 1px solid var(--line);
    background: white;
  }
  header h1 { margin: 0 0 4px; font-size: 20px; font-weight: 600; }
  header p  { margin: 0; color: var(--muted); font-size: 13px; }
  header a  { color: var(--accent); text-decoration: none; }

  .filter-bar {
    background: white;
    border-bottom: 1px solid var(--line);
    padding: 12px 24px;
  }
  .search-row {
    display: flex; gap: 12px; align-items: center; margin-bottom: 8px;
  }
  .search-row input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid var(--line-strong);
    border-radius: 6px;
    font-size: 14px;
    background: white;
  }
  .search-row input:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
  .count { font-size: 12px; color: var(--muted); white-space: nowrap; }
  .clear-btn {
    padding: 6px 10px;
    border: 1px solid var(--line-strong);
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
    color: var(--muted);
  }
  .clear-btn:hover { background: var(--row-hover); color: var(--fg); }

  details.filter-group {
    border: 1px solid var(--line);
    border-radius: 6px;
    margin-top: 8px;
    background: white;
  }
  details.filter-group summary {
    padding: 7px 12px;
    cursor: pointer;
    font-size: 12px;
    color: var(--muted);
    list-style: none;
    user-select: none;
  }
  details.filter-group summary::-webkit-details-marker { display: none; }
  details.filter-group summary::before {
    content: "▸ ";
    display: inline-block;
    transition: transform 0.15s;
  }
  details.filter-group[open] summary::before { transform: rotate(90deg); }
  details.filter-group summary span.active { color: var(--accent); font-weight: 600; }
  .chips {
    padding: 0 12px 10px;
    display: flex; flex-wrap: wrap; gap: 6px;
  }

  .chip, .pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    line-height: 1.6;
    background: #f2f4f7;
    color: #475467;
    border: 1px solid transparent;
    white-space: nowrap;
  }
  .chip {
    cursor: pointer;
    user-select: none;
    border: 1px solid var(--line-strong);
    background: white;
    color: #475467;
  }
  .chip:hover { background: var(--row-hover); }
  .chip.active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
  }
  .chip .ct { opacity: 0.6; margin-left: 4px; font-size: 10px; }

  /* group-colored pills */
  .g-hardware,  .g-physical  { background: #fee4e2; color: #b42318; }
  .g-movement                 { background: #fef0c7; color: #b54708; }
  .g-software                 { background: #e9d7fe; color: #6941c6; }
  .g-records                  { background: #d1fadf; color: #027a48; }
  .g-thinking, .g-cognitive   { background: #d1e9ff; color: #1849a9; }
  .g-business                 { background: #ccfbef; color: #115e59; }
  .g-data                     { background: #fce7ff; color: #9b1c8c; }
  .g-macro                    { background: #f2f4f7; color: #475467; }

  /* score badges within a tag pill */
  .pill .scores {
    margin-left: 6px;
    font-size: 9px;
    font-variant-numeric: tabular-nums;
    opacity: 0.75;
    letter-spacing: 0;
  }
  .pill .scores .sep { opacity: 0.5; margin: 0 1px; }
  .pill .scores .m::before { content: "m"; opacity: 0.65; }
  .pill .scores .i::before { content: "i"; opacity: 0.65; }
  /* Faded pill = primary axis is weakly held: average score < 2 */
  .pill.weak  { opacity: 0.55; }
  .pill.faint { opacity: 0.7; }
  /* status pill colors (for company status, not tag scores) */
  .status-acquired { background: #e9d7fe; color: #6941c6; }
  .status-defunct  { background: #fee4e2; color: #b42318; }
  .status-dormant  { background: #f2f4f7; color: #475467; }

  /* AI-level pill colors */
  .ai-ai-native    { background: #d1e9ff; color: #1849a9; }
  .ai-ai-adopting  { background: #d1fadf; color: #027a48; }
  .ai-ai-adjacent  { background: #f2f4f7; color: #475467; }
  .ai-standard-oss { background: #fef0c7; color: #b54708; }

  /* Maturity badge */
  .mat-public         { background: #1849a9; color: white; }
  .mat-late-stage     { background: #344054; color: white; }
  .mat-mid-stage      { background: #98a2b3; color: white; }
  .mat-early          { background: #fef0c7; color: #b54708; }
  .mat-stealth        { background: #475467; color: white; }
  .mat-mature-private { background: #d0d5dd; color: #344054; }
  .mat-standard       { background: #fef0c7; color: #b54708; }

  /* Pricing pill */
  .pricing-premium    { background: #ffe4e8; color: #b42318; }
  .pricing-mid        { background: #fef0c7; color: #b54708; }
  .pricing-economical { background: #d1fadf; color: #027a48; }
  .pricing-free       { background: #e9d7fe; color: #6941c6; }

  /* table */
  main { padding: 0 24px 24px; }
  .tbl-wrap {
    background: white;
    border: 1px solid var(--line);
    border-radius: 8px;
    overflow: auto;
    margin-top: 16px;
  }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    position: sticky; top: 0; z-index: 1;
    background: white;
    text-align: left;
    padding: 10px 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
    border-bottom: 1px solid var(--line);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
  }
  thead th:hover { color: var(--fg); }
  thead th.sorted { color: var(--accent); }
  thead th .hint {
    font-weight: 400;
    font-size: 9px;
    opacity: 0.65;
    text-transform: none;
    letter-spacing: 0;
    margin-left: 4px;
  }
  thead th.sorted::after {
    content: " ▾";
    font-size: 10px;
  }
  thead th.sorted.asc::after { content: " ▴"; }
  thead th.no-sort { cursor: default; }
  thead th.no-sort:hover { color: var(--muted); }

  tbody tr { border-bottom: 1px solid var(--line); }
  tbody tr:hover { background: var(--row-hover); }
  tbody tr:last-child { border-bottom: none; }
  tbody td {
    padding: 10px 12px;
    vertical-align: top;
    font-size: 13px;
  }
  tbody td.cell-tags { max-width: 240px; }
  tbody td.cell-tags .pill { margin: 2px 2px 0 0; cursor: pointer; }
  tbody td.cell-name {
    font-weight: 500;
    min-width: 160px;
  }
  tbody td.cell-name a {
    color: var(--fg);
    text-decoration: none;
  }
  tbody td.cell-name a:hover {
    color: var(--accent);
    text-decoration: underline;
  }
  tbody td.cell-name .unverified-mark {
    display: inline-block;
    margin-left: 4px;
    color: #b54708;
    font-size: 11px;
    cursor: help;
  }
  tbody td.cell-posture {
    font-style: italic;
    color: var(--muted);
    max-width: 200px;
  }
  tbody td.cell-notes {
    color: #475467;
    font-size: 12px;
    max-width: 320px;
  }

  td.cell-logo {
    width: 40px;
    padding: 8px 10px 8px 14px;
  }
  td.cell-logo img {
    width: 28px; height: 28px;
    object-fit: contain;
    border-radius: 4px;
    background: white;
    border: 1px solid var(--line);
  }
  td.cell-logo .placeholder {
    width: 28px; height: 28px;
    border-radius: 4px;
    background: #f2f4f7;
    border: 1px solid var(--line);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    color: var(--muted);
  }

  .empty-state {
    padding: 40px;
    text-align: center;
    color: var(--muted);
  }

  /* counts column right-aligned numbers */
  td.num, th.num { text-align: right; }

  /* footer */
  footer {
    margin-top: 32px;
    padding: 20px 24px;
    color: var(--muted);
    font-size: 12px;
    text-align: center;
  }
</style>
</head>
<body>

<header>
  <h1>Autonomous Science Landscape</h1>
  <p>
    A working catalog of <span id="company-total">…</span> companies in lab automation, autonomous science, and AI-for-bio.
    Source: Cheshire Labs landscape (May 2026).
    Views: <a href="companies.md">companies.md</a> · <a href="by-category.md">by-category</a> · <a href="by-thesis.md">by-thesis</a> · <a href="theses.md">theses</a> · <a href="README.md">README</a>.
  </p>
</header>

<div class="filter-bar">
  <div class="search-row">
    <input id="search" type="search" placeholder="Search name, posture, notes…" autocomplete="off">
    <span class="count" id="count">…</span>
    <button class="clear-btn" id="clear-btn" type="button">Clear filters</button>
  </div>
  <div id="filter-groups"></div>
</div>

<main>
  <div class="tbl-wrap">
    <table>
      <thead>
        <tr id="thead-row">
          <th class="no-sort"></th>
          <th data-sort="name">Company</th>
          <th data-sort="status">Status</th>
          <th data-sort="categories" class="num" title="Number of categories">Cat</th>
          <th class="no-sort">Categories <span class="hint">m·i</span></th>
          <th class="no-sort">Theses <span class="hint">m·i</span></th>
          <th data-sort="ai_level">AI level</th>
          <th data-sort="maturity">Maturity</th>
          <th data-sort="pricing">Pricing</th>
          <th data-sort="posture">Posture</th>
          <th class="no-sort">Notes</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="empty-state" id="empty" style="display:none">No companies match these filters.</div>
  </div>
</main>

<footer>
  Auto-generated. Edit <code>data/*.yaml</code> and run <code>python3 scripts/generate.py</code>.
</footer>

<script id="data-blob" type="application/json">__DATA_JSON__</script>
<script>
  const DATA = JSON.parse(document.getElementById("data-blob").textContent);

  document.getElementById("company-total").textContent = DATA.companies.length;

  const catByKey  = Object.fromEntries(DATA.categories.map(c => [c.key, c]));
  const thesByKey = Object.fromEntries(DATA.theses.map(t => [t.key, t]));

  const state = {
    search: "",
    filters: {
      categories: new Set(),
      theses: new Set(),
      ai_level: new Set(),
      maturity: new Set(),
      pricing: new Set(),
      status: new Set(),
    },
    sortBy: "name",
    sortDir: "asc",
  };

  // --- filter UI ---
  function buildFilterGroups() {
    const root = document.getElementById("filter-groups");
    const ctxs = [
      { key: "categories", label: "Categories",
        opts: DATA.categories.map(c => ({ value: c.key, label: c.name, group: c.group })) },
      { key: "theses", label: "Theses",
        opts: DATA.theses.map(t => ({ value: t.key, label: t.name, group: t.group })) },
      { key: "ai_level", label: "AI level",
        opts: ["ai-native","ai-adopting","ai-adjacent","standard-oss"].map(v => ({ value: v, label: v })) },
      { key: "maturity", label: "Maturity",
        opts: ["public","late-stage","mid-stage","early","stealth","mature-private","standard"].map(v => ({ value: v, label: v })) },
      { key: "pricing", label: "Pricing",
        opts: ["premium","mid","economical","free"].map(v => ({ value: v, label: v })) },
      { key: "status", label: "Status",
        opts: ["active","acquired","defunct","dormant"].map(v => ({ value: v, label: v })) },
    ];

    // Counts per option, computed against companies that pass *all other* filter groups.
    const counts = computeOptionCounts();

    ctxs.forEach(ctx => {
      const det = document.createElement("details");
      det.className = "filter-group";
      const sum = document.createElement("summary");
      sum.innerHTML = `${ctx.label} <span class="ct" id="ct-${ctx.key}"></span>`;
      det.appendChild(sum);
      const wrap = document.createElement("div");
      wrap.className = "chips";
      ctx.opts.forEach(opt => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "chip";
        btn.dataset.filterKey = ctx.key;
        btn.dataset.filterVal = opt.value;
        const ct = counts[ctx.key]?.[opt.value] ?? 0;
        btn.innerHTML = `${opt.label}<span class="ct">${ct}</span>`;
        if (state.filters[ctx.key].has(opt.value)) btn.classList.add("active");
        btn.addEventListener("click", () => toggleFilter(ctx.key, opt.value));
        wrap.appendChild(btn);
      });
      det.appendChild(wrap);
      root.appendChild(det);
    });
  }

  function refreshFilterCounts() {
    const counts = computeOptionCounts();
    document.querySelectorAll(".chip").forEach(chip => {
      const k = chip.dataset.filterKey;
      const v = chip.dataset.filterVal;
      const ct = counts[k]?.[v] ?? 0;
      chip.querySelector(".ct").textContent = ct;
      chip.classList.toggle("active", state.filters[k].has(v));
    });
    Object.keys(state.filters).forEach(k => {
      const n = state.filters[k].size;
      const el = document.getElementById(`ct-${k}`);
      if (!el) return;
      if (n > 0) {
        el.textContent = `· ${n} active`;
        el.classList.add("active");
      } else {
        el.textContent = "";
        el.classList.remove("active");
      }
    });
  }

  function toggleFilter(key, val) {
    const s = state.filters[key];
    if (s.has(val)) s.delete(val); else s.add(val);
    render();
  }

  // Helper: extract list of keys from a tag list (handles {k,m,i} objects)
  function tagKeys(arr) {
    if (!Array.isArray(arr)) return [];
    return arr.map(x => (typeof x === "string" ? x : x.k));
  }

  // For each filter axis, count companies that match all *other* axes plus the search.
  function computeOptionCounts() {
    const out = {};
    for (const k of Object.keys(state.filters)) {
      out[k] = {};
      for (const c of DATA.companies) {
        if (!matchesExcept(c, k)) continue;
        let arr = c[k];
        if (k === "status" && arr == null) arr = "active";
        let vs;
        if (k === "categories" || k === "theses") {
          vs = tagKeys(arr);
        } else {
          vs = Array.isArray(arr) ? arr : (arr != null ? [arr] : []);
        }
        for (const v of vs) out[k][v] = (out[k][v] || 0) + 1;
      }
    }
    return out;
  }
  function matchesExcept(c, exceptKey) {
    if (state.search) {
      const hay = [c.name, c.posture, c.notes].filter(Boolean).join(" ").toLowerCase();
      if (!hay.includes(state.search.toLowerCase())) return false;
    }
    for (const k of Object.keys(state.filters)) {
      if (k === exceptKey) continue;
      const sel = state.filters[k];
      if (sel.size === 0) continue;
      let cv = c[k];
      // status defaults to "active" if unset
      if (k === "status" && cv == null) cv = "active";
      let vs;
      if (k === "categories" || k === "theses") {
        vs = tagKeys(cv);
      } else {
        vs = Array.isArray(cv) ? cv : (cv != null ? [cv] : []);
      }
      if (vs.length === 0) return false;
      if (!vs.some(v => sel.has(v))) return false;
    }
    return true;
  }
  function matchesAll(c) {
    return matchesExcept(c, "__none__");
  }

  // --- table render ---
  function scoreSpan(m, i) {
    if (m == null && i == null) return "";
    return `<span class="scores"><span class="m">${m ?? "?"}</span><span class="sep">·</span><span class="i">${i ?? "?"}</span></span>`;
  }
  function tagWeakness(m, i) {
    // Visual fade for tags where the company is weakly held (avg < 2)
    const avg = ((m ?? 0) + (i ?? 0)) / 2;
    if (avg < 1) return "weak";
    if (avg < 2) return "faint";
    return "";
  }
  function pillCategory(item) {
    const key = (typeof item === "string") ? item : item.k;
    const m = (typeof item === "string") ? null : item.m;
    const i = (typeof item === "string") ? null : item.i;
    const c = catByKey[key]; if (!c) return "";
    const weakCls = tagWeakness(m, i);
    const tip = (m != null && i != null)
      ? `${c.name} — marketing emphasis ${m}/5, influence/maturity ${i}/5`
      : c.name;
    return `<span class="pill g-${c.group} ${weakCls}" data-pill="categories" data-val="${key}" title="${tip}">${c.name}${scoreSpan(m, i)}</span>`;
  }
  function pillThesis(item, primary) {
    const key = (typeof item === "string") ? item : item.k;
    const m = (typeof item === "string") ? null : item.m;
    const i = (typeof item === "string") ? null : item.i;
    const t = thesByKey[key]; if (!t) return "";
    const weakCls = tagWeakness(m, i);
    const label = primary ? `<strong>${t.name}</strong>` : t.name;
    const tip = (m != null && i != null)
      ? `${t.name} (${primary ? 'primary' : 'secondary'}) — marketing ${m}/5, influence ${i}/5`
      : `${t.name} (${primary ? 'primary' : 'secondary'})`;
    return `<span class="pill g-${t.group} ${weakCls}" data-pill="theses" data-val="${key}" title="${tip}">${label}${scoreSpan(m, i)}</span>`;
  }
  function pillSimple(field, value, classPrefix) {
    if (!value) return "";
    return `<span class="pill ${classPrefix}-${value}" data-pill="${field}" data-val="${value}">${value}</span>`;
  }
  function statusBadge(s) {
    if (!s || s === "active") return "";
    return `<span class="pill status-${s}" data-pill="status" data-val="${s}" title="${s}">${s}</span>`;
  }
  function logoCell(c) {
    if (c.logo_path) {
      return `<img src="${c.logo_path}" alt="" loading="lazy" onerror="this.outerHTML='<div class=&quot;placeholder&quot;>${(c.name[0]||'·').toUpperCase()}</div>'">`;
    }
    return `<div class="placeholder">${(c.name[0]||'·').toUpperCase()}</div>`;
  }

  function renderRow(c) {
    const cats = (c.categories || []).map(it => pillCategory(it)).join(" ");
    const thes = (c.theses || []).map((it, idx) => pillThesis(it, idx === 0)).join(" ");
    const nameCell = c.url
      ? `<a href="${c.url}" target="_blank" rel="noopener">${c.name}</a>`
      : c.name;
    const unverified = c.unverified
      ? `<span class="unverified-mark" title="Some fields are unverified">?</span>`
      : "";
    return `<tr>
      <td class="cell-logo">${logoCell(c)}</td>
      <td class="cell-name">${nameCell}${unverified}</td>
      <td>${statusBadge(c.status)}</td>
      <td class="num">${(c.categories || []).length}</td>
      <td class="cell-tags">${cats}</td>
      <td class="cell-tags">${thes}</td>
      <td>${pillSimple('ai_level', c.ai_level, 'ai')}</td>
      <td>${pillSimple('maturity', c.maturity, 'mat')}</td>
      <td>${pillSimple('pricing', c.pricing, 'pricing')}</td>
      <td class="cell-posture">${c.posture || ''}</td>
      <td class="cell-notes">${c.notes || ''}</td>
    </tr>`;
  }

  function sortKey(c) {
    const k = state.sortBy;
    if (k === "categories") return (c.categories || []).length;
    let v = c[k];
    if (Array.isArray(v)) v = v[0] || "";
    return (v ?? "").toString().toLowerCase();
  }

  function render() {
    const filtered = DATA.companies.filter(matchesAll);
    filtered.sort((a, b) => {
      const av = sortKey(a), bv = sortKey(b);
      if (av < bv) return state.sortDir === "asc" ? -1 : 1;
      if (av > bv) return state.sortDir === "asc" ? 1 : -1;
      return a.name.localeCompare(b.name);
    });

    const tbody = document.getElementById("tbody");
    tbody.innerHTML = filtered.map(renderRow).join("");
    document.getElementById("count").textContent =
      `${filtered.length} of ${DATA.companies.length} companies`;
    document.getElementById("empty").style.display = filtered.length ? "none" : "block";

    document.querySelectorAll("th[data-sort]").forEach(th => {
      th.classList.remove("sorted", "asc");
      if (th.dataset.sort === state.sortBy) {
        th.classList.add("sorted");
        if (state.sortDir === "asc") th.classList.add("asc");
      }
    });

    refreshFilterCounts();
  }

  // --- events ---
  document.getElementById("search").addEventListener("input", e => {
    state.search = e.target.value;
    render();
  });

  document.getElementById("clear-btn").addEventListener("click", () => {
    state.search = "";
    document.getElementById("search").value = "";
    Object.values(state.filters).forEach(s => s.clear());
    render();
  });

  document.querySelectorAll("th[data-sort]").forEach(th => {
    th.addEventListener("click", () => {
      const k = th.dataset.sort;
      if (state.sortBy === k) {
        state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
      } else {
        state.sortBy = k;
        state.sortDir = "asc";
      }
      render();
    });
  });

  // Click pill in table = toggle that filter
  document.getElementById("tbody").addEventListener("click", e => {
    const pill = e.target.closest(".pill[data-pill]");
    if (!pill) return;
    toggleFilter(pill.dataset.pill, pill.dataset.val);
  });

  buildFilterGroups();
  render();
</script>
</body>
</html>
"""


def gen_index_html(categories, theses, companies):
    # Attach actual logo path per company so the HTML can reference it directly.
    # Searches for {slug}.{png,svg,jpg,jpeg,webp,ico} in logos/.
    logo_exts = ("png", "svg", "jpg", "jpeg", "webp", "ico")
    enriched = []
    for c in companies:
        c2 = dict(c)
        slug = c["slug"]
        c2["logo_path"] = None
        for ext in logo_exts:
            if (LOGOS / f"{slug}.{ext}").exists():
                c2["logo_path"] = f"logos/{slug}.{ext}"
                break
        enriched.append(c2)
    data_json = json.dumps({
        "categories": categories,
        "theses": theses,
        "companies": enriched,
    }, default=str, separators=(",", ":"))
    html = (INDEX_HTML
            .replace("__BANNER__", BANNER_HTML)
            .replace("__DATA_JSON__", data_json))
    (ROOT / "index.html").write_text(html)


# ---------------------------------------------------------------------------
# markdown generators
# ---------------------------------------------------------------------------

def gen_readme(categories, theses, companies):
    cat_idx = _index(categories)
    th_idx = _index(theses)
    cat_count = _company_count_by(companies, "categories")
    thes_count = _company_count_by(companies, "theses")
    ai_count = Counter(c.get("ai_level") for c in companies if c.get("ai_level"))
    maturity_count = Counter(c.get("maturity") for c in companies if c.get("maturity"))
    unverified_count = sum(1 for c in companies if c.get("unverified"))

    lines = [
        BANNER_MD,
        "",
        "# Autonomous Science Landscape",
        "",
        f"Working catalog of **{len(companies)} companies** in lab automation, autonomous science, and AI-for-bio. ",
        f"Each is tagged with the functional category it occupies *and* the implicit thesis it holds about why lab automation hasn't gone the way of self-driving.",
        "",
        f"Source v1: Cheshire Labs landscape image (May 2026). **{unverified_count} entries have unverified fields** — flagged with `unverified: true` in the data.",
        "",
        "## Views",
        "",
        "| File | What it is |",
        "|---|---|",
        "| [`index.html`](./index.html) | **Sortable, filterable HTML view with logos, tag pills, and per-column filters. Open this first.** |",
        "| [`companies.md`](./companies.md) | Master table — one row per company |",
        "| [`by-category.md`](./by-category.md) | Companies grouped by Cheshire-style category |",
        "| [`by-thesis.md`](./by-thesis.md) | Companies grouped by which bottleneck thesis they hold |",
        "| [`theses.md`](./theses.md) | Each thesis written up — bet, predicts, falsifier |",
        "| [`companies.csv`](./companies.csv) | Same data, machine-readable |",
        "",
        "## Architecture",
        "",
        "**Data is the source of truth.** Edit YAML; regenerate everything else.",
        "",
        "```",
        "data/",
        "├── companies.yaml      ← edit me",
        "├── categories.yaml     ← edit me",
        "└── theses.yaml         ← edit me",
        "scripts/",
        "└── generate.py         ← run me",
        "logos/                  ← cached per-company logos (favicons sz=128)",
        "```",
        "",
        "Regenerate everything:",
        "",
        "```",
        "python3 scripts/generate.py                  # rebuild MDs + HTML",
        "python3 scripts/generate.py --fetch-logos    # also download missing logos",
        "```",
        "",
        "## Tag legend",
        "",
        "### `ai_level`",
        "",
        "| Value | Meaning |",
        "|---|---|",
        "| `ai-native` | Founded around an AI/ML thesis; product makes no sense without modern ML |",
        "| `ai-adopting` | Traditional product surface, actively bolting on AI features |",
        "| `ai-adjacent` | Instrument/software where AI is marketing veneer, not core |",
        "| `standard-oss` | A specification or open project, not a company |",
        "",
        "### `maturity`",
        "",
        "`public` · `late-stage` · `mid-stage` · `early` · `stealth` · `mature-private` · `standard`",
        "",
        "### `pricing`",
        "",
        "`premium` (instrument-list-price tier; 6-figure pharma quote) · `mid` (Series-A biotech / academic core) · `economical` (designed to undercut on capex) · `free` (OSS / standard)",
        "",
        "## At a glance",
        "",
        f"- **Companies:** {len(companies)}",
        f"- **Categories used:** {len(cat_count)} of {len(categories)}",
        f"- **Theses held:** {len(thes_count)} of {len(theses)}",
        "",
        "**By AI level:**",
        "",
    ]
    for level, n in ai_count.most_common():
        lines.append(f"- `{level}` — {n}")
    lines.append("")
    lines.append("**By maturity:**")
    lines.append("")
    for m, n in maturity_count.most_common():
        lines.append(f"- `{m}` — {n}")
    lines.append("")
    lines += [
        "## Methodology & open questions",
        "",
        "Sources for v1: Cheshire Labs landscape image, public company sites, generally-known field knowledge as of training cutoff. No primary research yet.",
        "",
        "**What needs verification:**",
        "",
        "- Maturity / funding stage (drift-prone)",
        "- Thesis assignments — inferred from public posture, not stated; worth confirming via founder talks/blog posts",
        "- Companies couldn't be fully resolved from the image alone — see entries with `unverified: true`",
        "",
        "**Worth adding next:**",
        "",
        "- Founders / team size",
        "- Last public funding round + investors",
        "- Citation count / public talks (proxy for influence)",
        "- Customer logos disclosed",
        "- Open-source surface (does the company publish code? specs?)",
        "- Geography (US / UK / EU / JP) — there's a real cluster pattern",
        "",
    ]
    (ROOT / "README.md").write_text("\n".join(lines))


def _fmt_tag_md(item, idx) -> str:
    """Format a tag item for markdown — '<name> (m4/i2)'."""
    k = tag_key(item)
    name = idx[k]["name"] if k in idx else k
    m, i = tag_score(item)
    if m is None and i is None:
        return name
    return f"{name} (m{m}/i{i})"


def gen_companies_md(categories, theses, companies):
    cat_idx = _index(categories)
    th_idx = _index(theses)

    lines = [
        BANNER_MD,
        "",
        "# Master company table",
        "",
        f"{len(companies)} companies. One row each. Multi-value fields use `; `. ",
        "Per-tag scores `(mN/iN)` are **marketing emphasis** (how loud they are about it) and **influence/maturity** (actual track record), each 0–5.",
        "",
        "For sortable / filterable views, use [`index.html`](./index.html).",
        "",
        "| Company | Status | Categories | Theses (primary first) | AI level | Maturity | Customer | Pricing | Posture | Notes |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    sorted_co = sorted(companies, key=lambda c: c["name"].lower())
    for c in sorted_co:
        cats = "; ".join(_fmt_tag_md(it, cat_idx) for it in (c.get("categories") or [])) or "—"
        thes = "; ".join(_fmt_tag_md(it, th_idx) for it in (c.get("theses") or [])) or "—"
        custs = "; ".join(c.get("customers") or []) or "—"
        flag = " <sup>?</sup>" if c.get("unverified") else ""
        nm = c["name"] + flag
        if c.get("url"):
            nm = f"[{nm}]({c['url']})"
        status = c.get("status") or "active"
        lines.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            nm,
            status,
            _md_escape(cats),
            _md_escape(thes),
            c.get("ai_level") or "—",
            c.get("maturity") or "—",
            _md_escape(custs),
            c.get("pricing") or "—",
            _md_escape(c.get("posture") or "—"),
            _md_escape(c.get("notes") or ""),
        ))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Quick stats")
    lines.append("")
    ai_count = Counter(c.get("ai_level") for c in companies if c.get("ai_level"))
    status_count = Counter(c.get("status") or "active" for c in companies)
    lines.append(f"- **Total:** {len(companies)} companies")
    for level, n in ai_count.most_common():
        lines.append(f"- **{level}:** {n}")
    lines.append("")
    lines.append("**By status:**")
    for s, n in status_count.most_common():
        lines.append(f"- `{s}`: {n}")
    lines.append("")
    most_cats = sorted(companies, key=lambda c: -len(c.get("categories") or []))[:3]
    lines.append("**Broadest claims (most categories):**")
    for c in most_cats:
        lines.append(f"- {c['name']} — {len(c.get('categories') or [])} categories")
    lines.append("")
    (ROOT / "companies.md").write_text("\n".join(lines))


def gen_by_category_md(categories, theses, companies):
    lines = [BANNER_MD, "", "# By category", "",
             "Companies grouped by functional category. A company in multiple categories appears in each. ",
             "Score format: **m**arketing emphasis · **i**nfluence/maturity, both 0–5.",
             "Each category lists its companies sorted by influence (descending), then marketing.",
             ""]
    by_cat: dict[str, list[tuple]] = defaultdict(list)
    for c in companies:
        for item in c.get("categories") or []:
            k = tag_key(item)
            m, i = tag_score(item)
            by_cat[k].append((c, m or 0, i or 0))

    for cat in categories:
        rows = sorted(by_cat.get(cat["key"], []), key=lambda r: (-r[2], -r[1], r[0]["name"].lower()))
        lines.append(f"## {cat['name']}")
        lines.append("")
        lines.append(f"> {cat['one_liner']}")
        lines.append("")
        if cat.get("commentary"):
            lines.append(cat["commentary"].strip())
            lines.append("")
        if not rows:
            lines.append("_no companies tagged_")
            lines.append("")
            continue
        lines.append(f"**{len(rows)} companies, sorted by influence:**")
        lines.append("")
        for c, m, i in rows:
            status = c.get("status") or "active"
            status_tag = "" if status == "active" else f" `[{status}]`"
            lines.append(f"- **{c['name']}**{status_tag} — m{m}/i{i} — {c.get('posture') or ''}")
        lines.append("")
    (ROOT / "by-category.md").write_text("\n".join(lines))


def gen_by_thesis_md(categories, theses, companies):
    lines = [BANNER_MD, "", "# By thesis", "",
             "Companies grouped by which bottleneck thesis they hold. ",
             "Score format: **m**arketing emphasis · **i**nfluence/maturity, both 0–5.",
             "",
             "*Two density numbers per thesis:* **marketing-weighted** (sum of m-scores) shows how loud a narrative is; **influence-weighted** (sum of i-scores) shows how much actual track record sits behind it. ",
             "Loud narratives with low influence sums are early-stage hype; quiet ones with high influence are established but invisible.",
             ""]
    # Group: list of (company, m, i, primary)
    by_thes: dict[str, list] = defaultdict(list)
    for c in companies:
        for idx, item in enumerate(c.get("theses") or []):
            k = tag_key(item)
            m, i = tag_score(item)
            by_thes[k].append((c, m or 0, i or 0, idx == 0))

    # Order theses by total influence (desc), so highest-track-record first
    def _i_sum(th):
        return sum(r[2] for r in by_thes.get(th["key"], []))
    def _m_sum(th):
        return sum(r[1] for r in by_thes.get(th["key"], []))
    th_sorted = sorted(theses, key=lambda t: (-_i_sum(t), -_m_sum(t)))

    for th in th_sorted:
        rows = by_thes.get(th["key"], [])
        n = len(rows)
        m_sum = sum(r[1] for r in rows)
        i_sum = sum(r[2] for r in rows)
        # Sort holders by influence then marketing
        rows_sorted = sorted(rows, key=lambda r: (-r[2], -r[1], r[0]["name"].lower()))
        gap = m_sum - i_sum
        gap_label = (
            "narrative outrunning track record" if gap >= 6 else
            "narrative ahead of track record"     if gap >= 3 else
            "balanced"                            if abs(gap) < 3 else
            "track record outrunning narrative"   if gap >= -6 else
            "established but quiet"
        )
        lines.append(f"## {th['name']}")
        lines.append("")
        lines.append(f"> {th['bet'].strip()}")
        lines.append("")
        lines.append(f"**{n} holders** · marketing-weighted **{m_sum}** · influence-weighted **{i_sum}** · _{gap_label}_")
        lines.append("")
        if not rows_sorted:
            lines.append("_no companies hold this thesis_")
            lines.append("")
            continue
        for c, m, i, primary in rows_sorted:
            status = c.get("status") or "active"
            status_tag = "" if status == "active" else f" `[{status}]`"
            prim = "**[primary]** " if primary else ""
            lines.append(f"- {prim}**{c['name']}**{status_tag} — m{m}/i{i} — {c.get('posture') or ''}")
        lines.append("")

    # Density ranking
    lines.append("---")
    lines.append("")
    lines.append("## Density ranking")
    lines.append("")
    lines.append("| Thesis | Holders | Marketing-weighted | Influence-weighted | Gap (m − i) |")
    lines.append("|---|---:|---:|---:|---:|")
    rank_rows = []
    for th in theses:
        rows = by_thes.get(th["key"], [])
        m_sum = sum(r[1] for r in rows)
        i_sum = sum(r[2] for r in rows)
        rank_rows.append((th["name"], len(rows), m_sum, i_sum, m_sum - i_sum))
    rank_rows.sort(key=lambda r: -r[2])  # by marketing-weighted
    for r in rank_rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]:+d} |")
    lines.append("")
    lines.append("_Sorted by marketing-weighted total — top rows are the loudest narratives._")
    lines.append("")
    (ROOT / "by-thesis.md").write_text("\n".join(lines))


def gen_theses_md(theses, companies):
    by_thes: dict[str, list] = defaultdict(list)
    for c in companies:
        for idx, item in enumerate(c.get("theses") or []):
            k = tag_key(item)
            m, i = tag_score(item)
            by_thes[k].append((c, m or 0, i or 0, idx == 0))

    lines = [BANNER_MD, "", "# Theses", "",
             "Why isn't lab automation more widespread? Each company implicitly answers. ",
             "Below: bet, what it predicts, what would falsify it, and who holds it (sorted by influence).",
             ""]
    for th in theses:
        rows = by_thes.get(th["key"], [])
        rows_sorted = sorted(rows, key=lambda r: (-r[2], -r[1], r[0]["name"].lower()))
        lines.append(f"## {th['name']}")
        lines.append("")
        lines.append(f"> {th['bet'].strip()}")
        lines.append("")
        lines.append("**Predicts:** " + th["predicts"].strip().replace("\n", " "))
        lines.append("")
        lines.append("**Falsifier:** " + th["falsifier"].strip().replace("\n", " "))
        lines.append("")
        if not rows_sorted:
            lines.append("_(no companies hold this thesis)_")
            lines.append("")
            continue
        lines.append("**Holders (influence-sorted):**")
        lines.append("")
        for c, m, i, primary in rows_sorted:
            status = c.get("status") or "active"
            status_tag = "" if status == "active" else f" `[{status}]`"
            prim = "★ " if primary else ""
            lines.append(f"- {prim}{c['name']}{status_tag} — m{m}/i{i}")
        lines.append("")
    (ROOT / "theses.md").write_text("\n".join(lines))


def _tag_csv(items) -> str:
    """Render a tag list for CSV: 'cat1:m4/i5; cat2:m3/i2'."""
    out = []
    for it in items or []:
        k = tag_key(it)
        m, i = tag_score(it)
        if m is None and i is None:
            out.append(k)
        else:
            out.append(f"{k}:m{m}/i{i}")
    return "; ".join(out)


def gen_companies_csv(companies):
    cols = ["name", "slug", "domain", "url", "categories", "theses",
            "ai_level", "maturity", "customers", "pricing", "status", "posture", "notes", "unverified"]
    with open(ROOT / "companies.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for c in sorted(companies, key=lambda c: c["name"].lower()):
            row = []
            for k in cols:
                v = c.get(k)
                if k in ("categories", "theses"):
                    v = _tag_csv(v)
                elif k == "status":
                    v = v or "active"
                elif isinstance(v, list):
                    v = "; ".join(v)
                row.append("" if v is None else v)
            w.writerow(row)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-logos", action="store_true",
                        help="Download missing logos (favicons sz=128) into logos/.")
    parser.add_argument("--force-logos", action="store_true",
                        help="Re-download all logos, overwriting existing.")
    args = parser.parse_args()

    cats, theses, companies = load_data()
    validate(cats, theses, companies)
    print(f"loaded: {len(companies)} companies, {len(cats)} categories, {len(theses)} theses")

    if args.fetch_logos or args.force_logos:
        print("fetching logos...")
        fetch_logos(companies, force=args.force_logos)

    print("generating views...")
    gen_index_html(cats, theses, companies)
    gen_readme(cats, theses, companies)
    gen_companies_md(cats, theses, companies)
    gen_by_category_md(cats, theses, companies)
    gen_by_thesis_md(cats, theses, companies)
    gen_theses_md(theses, companies)
    gen_companies_csv(companies)
    print("done.")


if __name__ == "__main__":
    main()
