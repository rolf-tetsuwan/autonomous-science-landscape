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


def validate(categories, theses, companies) -> None:
    cat_keys = {c["key"] for c in categories}
    thesis_keys = {t["key"] for t in theses}
    errors: list[str] = []
    for c in companies:
        for k in c.get("categories") or []:
            if k not in cat_keys:
                errors.append(f"{c['name']}: unknown category '{k}'")
        for k in c.get("theses") or []:
            if k not in thesis_keys:
                errors.append(f"{c['name']}: unknown thesis '{k}'")
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
    """Count companies that have a given key in a list-typed field."""
    counter: Counter = Counter()
    for c in companies:
        for k in c.get(field) or []:
            counter[k] += 1
    return counter


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
          <th data-sort="categories" class="num">Cat</th>
          <th class="no-sort">Categories</th>
          <th class="no-sort">Theses</th>
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

  // For each filter axis, count companies that match all *other* axes plus the search.
  function computeOptionCounts() {
    const out = {};
    for (const k of Object.keys(state.filters)) {
      out[k] = {};
      for (const c of DATA.companies) {
        if (!matchesExcept(c, k)) continue;
        const vs = Array.isArray(c[k]) ? c[k] : (c[k] != null ? [c[k]] : []);
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
      const cv = c[k];
      if (Array.isArray(cv)) {
        if (!cv.some(v => sel.has(v))) return false;
      } else {
        if (!sel.has(cv)) return false;
      }
    }
    return true;
  }
  function matchesAll(c) {
    return matchesExcept(c, "__none__");
  }

  // --- table render ---
  function pillCategory(key) {
    const c = catByKey[key]; if (!c) return "";
    return `<span class="pill g-${c.group}" data-pill="categories" data-val="${key}">${c.name}</span>`;
  }
  function pillThesis(key, primary) {
    const t = thesByKey[key]; if (!t) return "";
    const label = primary ? `<strong>${t.name}</strong>` : t.name;
    return `<span class="pill g-${t.group}" data-pill="theses" data-val="${key}" title="${primary ? 'primary' : 'secondary'}">${label}</span>`;
  }
  function pillSimple(field, value, classPrefix) {
    if (!value) return "";
    return `<span class="pill ${classPrefix}-${value}" data-pill="${field}" data-val="${value}">${value}</span>`;
  }
  function logoCell(c) {
    if (c.logo_path) {
      return `<img src="${c.logo_path}" alt="" loading="lazy" onerror="this.outerHTML='<div class=&quot;placeholder&quot;>${(c.name[0]||'·').toUpperCase()}</div>'">`;
    }
    return `<div class="placeholder">${(c.name[0]||'·').toUpperCase()}</div>`;
  }

  function renderRow(c) {
    const cats = (c.categories || []).map(k => pillCategory(k)).join(" ");
    const thes = (c.theses || []).map((k, i) => pillThesis(k, i === 0)).join(" ");
    const nameCell = c.url
      ? `<a href="${c.url}" target="_blank" rel="noopener">${c.name}</a>`
      : c.name;
    const unverified = c.unverified
      ? `<span class="unverified-mark" title="Some fields are unverified">?</span>`
      : "";
    return `<tr>
      <td class="cell-logo">${logoCell(c)}</td>
      <td class="cell-name">${nameCell}${unverified}</td>
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


def gen_companies_md(categories, theses, companies):
    cat_idx = _index(categories)
    th_idx = _index(theses)

    lines = [
        BANNER_MD,
        "",
        "# Master company table",
        "",
        f"{len(companies)} companies. One row each. Multi-value fields use `; `. `?` after a name flags entries with unverified fields.",
        "",
        "For sortable / filterable views, use [`index.html`](./index.html).",
        "",
        "| Company | Categories | Theses (primary first) | AI level | Maturity | Customer | Pricing | Posture | Notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    sorted_co = sorted(companies, key=lambda c: c["name"].lower())
    for c in sorted_co:
        cats = "; ".join(cat_idx[k]["name"] for k in (c.get("categories") or []) if k in cat_idx) or "—"
        thes = "; ".join(th_idx[k]["name"] for k in (c.get("theses") or []) if k in th_idx) or "—"
        custs = "; ".join(c.get("customers") or []) or "—"
        flag = " <sup>?</sup>" if c.get("unverified") else ""
        nm = c["name"] + flag
        if c.get("url"):
            nm = f"[{nm}]({c['url']})"
        lines.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            nm,
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
    lines.append(f"- **Total:** {len(companies)} companies")
    for level, n in ai_count.most_common():
        lines.append(f"- **{level}:** {n}")
    cat_count = _company_count_by(companies, "categories")
    most_cats = sorted(companies, key=lambda c: -len(c.get("categories") or []))[:3]
    lines.append("")
    lines.append("**Broadest claims (most categories):**")
    for c in most_cats:
        lines.append(f"- {c['name']} — {len(c.get('categories') or [])} categories")
    lines.append("")
    (ROOT / "companies.md").write_text("\n".join(lines))


def gen_by_category_md(categories, theses, companies):
    lines = [BANNER_MD, "", "# By category", "",
             "Companies grouped by Cheshire-style functional category. A company in multiple categories appears in each.", ""]
    by_cat: dict[str, list] = defaultdict(list)
    for c in companies:
        for k in c.get("categories") or []:
            by_cat[k].append(c)

    for cat in categories:
        in_cat = sorted(by_cat.get(cat["key"], []), key=lambda c: c["name"].lower())
        lines.append(f"## {cat['name']}")
        lines.append("")
        lines.append(f"> {cat['one_liner']}")
        lines.append("")
        if cat.get("commentary"):
            lines.append(cat["commentary"].strip())
            lines.append("")
        if not in_cat:
            lines.append("_no companies tagged_")
            lines.append("")
            continue
        lines.append(f"**{len(in_cat)} companies:** " + ", ".join(c["name"] for c in in_cat))
        lines.append("")
    (ROOT / "by-category.md").write_text("\n".join(lines))


def gen_by_thesis_md(categories, theses, companies):
    lines = [BANNER_MD, "", "# By thesis", "",
             "Companies grouped by which bottleneck thesis they hold. **Primary** = first thesis listed in their record. ",
             "Most companies hold 2–3.", "",
             "*A thesis with many companies is a crowded narrative; a thesis with few is either contrarian or under-served.*", ""]
    primary_by_thes: dict[str, list] = defaultdict(list)
    secondary_by_thes: dict[str, list] = defaultdict(list)
    for c in companies:
        for i, k in enumerate(c.get("theses") or []):
            (primary_by_thes if i == 0 else secondary_by_thes)[k].append(c)

    # Render each thesis ordered by total holders desc.
    th_with_count = sorted(
        theses,
        key=lambda t: -(len(primary_by_thes.get(t["key"], [])) + len(secondary_by_thes.get(t["key"], []))),
    )
    for th in th_with_count:
        prim = sorted(primary_by_thes.get(th["key"], []), key=lambda c: c["name"].lower())
        sec = sorted(secondary_by_thes.get(th["key"], []), key=lambda c: c["name"].lower())
        total = len(prim) + len(sec)
        crowd = (
            "**very crowded**" if total >= 8 else
            "**crowded**" if total >= 6 else
            "moderate" if total >= 4 else
            "thin" if total >= 2 else
            "**very thin**"
        )
        lines.append(f"## {th['name']}")
        lines.append("")
        lines.append(f"> {th['bet'].strip()}")
        lines.append("")
        lines.append(f"**Holders: {total} total** ({crowd}) — {len(prim)} primary, {len(sec)} secondary")
        lines.append("")
        if prim:
            lines.append("**Primary holders:** " + ", ".join(c["name"] for c in prim))
        if sec:
            lines.append("**Secondary holders:** " + ", ".join(c["name"] for c in sec))
        if not prim and not sec:
            lines.append("_no companies holding this thesis_")
        lines.append("")

    # Density ranking
    lines.append("---")
    lines.append("")
    lines.append("## Density ranking")
    lines.append("")
    lines.append("| Thesis | Total holders | Primary | Secondary | Crowdedness |")
    lines.append("|---|---:|---:|---:|---|")
    rows = []
    for th in theses:
        prim = primary_by_thes.get(th["key"], [])
        sec = secondary_by_thes.get(th["key"], [])
        total = len(prim) + len(sec)
        crowd = (
            "very crowded" if total >= 8 else
            "crowded" if total >= 6 else
            "moderate" if total >= 4 else
            "thin" if total >= 2 else
            "very thin"
        )
        rows.append((th["name"], total, len(prim), len(sec), crowd))
    rows.sort(key=lambda r: -r[1])
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    lines.append("")
    (ROOT / "by-thesis.md").write_text("\n".join(lines))


def gen_theses_md(theses, companies):
    primary_by_thes: dict[str, list] = defaultdict(list)
    secondary_by_thes: dict[str, list] = defaultdict(list)
    for c in companies:
        for i, k in enumerate(c.get("theses") or []):
            (primary_by_thes if i == 0 else secondary_by_thes)[k].append(c)

    lines = [BANNER_MD, "", "# Theses", "",
             "Why isn't lab automation more widespread? Each company implicitly answers. Below: bet, what it predicts, what would falsify it, and who currently holds it.",
             ""]
    for th in theses:
        prim = sorted(primary_by_thes.get(th["key"], []), key=lambda c: c["name"].lower())
        sec = sorted(secondary_by_thes.get(th["key"], []), key=lambda c: c["name"].lower())
        lines.append(f"## {th['name']}")
        lines.append("")
        lines.append(f"> {th['bet'].strip()}")
        lines.append("")
        lines.append("**Predicts:** " + th["predicts"].strip().replace("\n", " "))
        lines.append("")
        lines.append("**Falsifier:** " + th["falsifier"].strip().replace("\n", " "))
        lines.append("")
        if prim:
            lines.append("**Primary holders:** " + ", ".join(c["name"] for c in prim))
        if sec:
            lines.append("**Secondary holders:** " + ", ".join(c["name"] for c in sec))
        if not prim and not sec:
            lines.append("_(no companies in dataset hold this thesis)_")
        lines.append("")
    (ROOT / "theses.md").write_text("\n".join(lines))


def gen_companies_csv(companies):
    cols = ["name", "slug", "domain", "url", "categories", "theses",
            "ai_level", "maturity", "customers", "pricing", "posture", "notes", "unverified"]
    with open(ROOT / "companies.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for c in sorted(companies, key=lambda c: c["name"].lower()):
            row = []
            for k in cols:
                v = c.get(k)
                if isinstance(v, list):
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
