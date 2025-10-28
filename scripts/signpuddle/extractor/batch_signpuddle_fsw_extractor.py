#!/usr/bin/env python3
"""
Extract Formal SignWriting (FSW) strings from SignPuddle for a selected
dictionary (country code) and write a CSV with: canonical_gloss, synonyms,
sid, and FSW.
"""

import argparse
import os, sys, re, time, csv
import requests, pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, quote_plus

__version__ = "2.0.0"  # single source of truth

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
BASE = 'https://www.signbank.org/signpuddle2.0/'
LANG_TABLE = "signpuddle_language_codes.csv"

DEFAULT_BATCH_SIZE = 10000
REQUEST_TIMEOUT = (10, 120)     # per batch page
INDEX_TIMEOUT = 60       # for large index pages
RATE_DELAY = 0.25
MAX_ATTEMPTS = 3

# dash-like characters (– — - − etc.)
_DASH_CHARS = "-\u2010\u2011\u2012\u2013\u2014\u2212"
_DASH_RE = re.compile(f"[{re.escape(_DASH_CHARS)}]")

def _dashless(s: str) -> str:
    """Remove any dash/hyphen variants."""
    return _DASH_RE.sub("", s or "")

# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--cc", help="Country code (dashless, e.g., US, KR, CAfr, CHfr)")
    p.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                   help=f"Batch size for requests (default: {DEFAULT_BATCH_SIZE})")
    p.add_argument("--version", action="version",
                   version=f"%(prog)s {__version__}")
    return p.parse_args()

# ─────────────────────────────────────────────
# COUNTRY SELECTION
# ─────────────────────────────────────────────
def load_lang() -> pd.DataFrame:
    """Load country-language mappings from CSV."""
    df = pd.read_csv(LANG_TABLE)
    exp = ["country_code","country","ui","sgn"]
    if not all(c in df.columns for c in exp):
        df = df.iloc[:, :4]; df.columns = exp
    df["country_display"] = df["country_code"].astype(str).map(_dashless)
    # Sort alphabetically by dashless code (we don't print "(sorted)")
    df = df.sort_values("country_display", key=lambda s: s.str.lower()).reset_index(drop=True)
    return df[["country_code","country","ui","sgn","country_display"]]

def pick_country(df: pd.DataFrame, code: str|None):
    print("\nAvailable SignPuddle Language Options")
    print(" country_code        country               ui  sgn")
    for _, r in df.iterrows():
        print(f" {r['country_display']:<20}{r['country']:<20}{r['ui']:>2}  {r['sgn']}")
    code = code or input("\nEnter country code: ").strip()
    norm = _dashless(code).lower()
    m = df[df["country_display"].str.lower().eq(norm)]
    if m.empty:
        sys.exit(f"❌ Invalid country code '{code}'.")
    r = m.iloc[0]
    return dict(ui=int(r.ui), sgn=int(r.sgn), country=r.country, code=r.country_code, clean=r.country_display)

# ─────────────────────────────────────────────
# HTTP SESSION
# ─────────────────────────────────────────────
sess = requests.Session()
sess.headers.update({
    "User-Agent": "SignPuddleScraper/2.0 (+contact=you@example.com)",
    # avoid gzip/chunked quirks on some large pages
    "Accept-Encoding": "identity",
})

# ─────────────────────────────────────────────
# SID LIST FETCH (announce bulk/no-bulk, show 60s notice)
# ─────────────────────────────────────────────
def get_sids(ui:int, sgn:int, country:str|None=None) -> list[str]:
    """Fetch SID list, announce bulk/no-bulk, then count, and ask to proceed."""
    url = f"{BASE}searchword.php?ui={ui}&sgn={sgn}&sTrm=*"
    label = country or f"ui={ui}, sgn={sgn}"
    attempt = 1
    while True:
        try:
            time.sleep(RATE_DELAY)
            print(f"\nFetching index page for {label} ...", flush=True)
            print(f"⏳ Waiting for server response (up to {INDEX_TIMEOUT}s before next attempt)", flush=True)
            r = sess.get(url, timeout=INDEX_TIMEOUT)
            r.raise_for_status()
            break
        except Exception as e:
            if attempt >= MAX_ATTEMPTS:
                raise
            wait = 0.5 * (2 ** (attempt - 1))
            print(f"Index fetch error: {e} — retrying in {wait:.1f}s (attempt {attempt}/{MAX_ATTEMPTS})",
                  flush=True)
            time.sleep(wait)
            attempt += 1

    soup = BeautifulSoup(r.text, 'lxml')

    # Check for bulk-SID link first (fast)
    pl = soup.find('a', href=lambda h: h and 'print?puddle=sgn' in h)
    if pl:
        print("\n✅ Found bulk-SID link. Counting entries...", flush=True)
        ids_str = parse_qs(urlparse(pl['href']).query).get('ids', [''])[0]
        ids = [i for i in ids_str.split(',') if i]
        print(f"📋 Total: {len(ids):,} entries.", flush=True)
    else:
        print("\n⚠️  No bulk-SID link found.", flush=True)
        seen = set()
        anchors = soup.find_all('a', href=lambda h: h and 'searchword.php' in h and 'sid=' in h)
        for a in anchors:
            raw = parse_qs(urlparse(a['href']).query).get('sid', [''])[0]
            for s in raw.split(','):
                if s:
                    seen.add(s)
        ids = list(seen)
        print(f"📋 Found {len(ids):,} SIDs by scanning index page.", flush=True)

    # Always confirm before continuing
    proceed = input(f"\nProceed with fetching all {len(ids):,} entries? (y/n): ").strip().lower()
    if proceed not in {"y", "yes"}:
        print("Aborted by user.")
        sys.exit(0)

    return ids

# ─────────────────────────────────────────────
# FETCHING
# ─────────────────────────────────────────────
def batches(sids:list[str], n:int) -> list[list[str]]:
    return [sids[i:i+n] for i in range(0, len(sids), n)]

def fetch_batch(ui:int, sgn:int, batch:list[str]) -> list[dict]:
    time.sleep(RATE_DELAY)
    url = f"{BASE}searchword.php?ui={ui}&sgn={sgn}&sid={quote_plus(','.join(batch))}&sTrm=*"
    r = sess.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')

    rows = []
    for tbl in soup.find_all('table', attrs={'cellpadding':'10'}):
        cell = tbl.find('td'); small = tbl.find_next('small')
        if not cell or not small:
            raise RuntimeError("Unexpected table structure")
        canonical = cell.find('font', size='+1').get_text(strip=True)
        parts = cell.get_text("||", strip=True).split("||")
        synonyms = parts[1] if len(parts) > 1 else ''
        a = small.find('a', href=lambda h: h and 'canvas.php' in h)
        sid = parse_qs(urlparse(a['href']).query)['sid'][0]

        # FSW extraction: find "FSW:" label → next span
        fsw = None; found = False
        for node in small.descendants:
            if isinstance(node, str) and 'FSW:' in node:
                found = True
            elif found and getattr(node, "name", None) == 'span':
                fsw = node.get_text(strip=True)
                break
        if not fsw:
            span = small.find('span')
            if span:
                fsw = span.get_text(strip=True) or None

        rows.append({'canonical_gloss': canonical,
                     'synonyms': synonyms,
                     'sid': sid,
                     'FSW': fsw})
    return rows

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    args = parse_args()
    batch_size = args.batch_size

    print(f"SignPuddle FSW Extractor v{__version__}")
    print("Extracts FSW entries from SignPuddle for a selected dictionary and writes a CSV.\n")

    lang = load_lang()
    sel = pick_country(lang, args.cc)
    ui, sgn = sel["ui"], sel["sgn"]
    out = f"all_ui{ui}_sgn{sgn}_fsw_{sel['clean']}.csv"
    print(f"\nUsing {sel['country']} ({sel['code']}) → ui={ui}, sgn={sgn}")
    print(f"Output: {out}")

    sids = get_sids(ui, sgn, sel["country"])
    total_batches = (len(sids) + batch_size - 1) // batch_size
    print(f"\nFound {len(sids):,} SIDs. Fetching in {total_batches} batch(es) of {batch_size}…\n")

    if os.path.exists(out):
        os.remove(out)
    header_written = False

    for i, batch in enumerate(batches(sids, batch_size), 1):
        attempt = 1
        while True:
            try:
                rows = fetch_batch(ui, sgn, batch)
                print(f"[{i}/{total_batches}] {len(rows)} rows")
                pd.DataFrame(rows).to_csv(
                    out, mode='a', header=not header_written, index=False, quoting=csv.QUOTE_MINIMAL
                )
                header_written = True
                break
            except Exception as e:
                if attempt >= MAX_ATTEMPTS:
                    raise
                wait = 0.5 * (2 ** (attempt - 1))
                print(f"[{i}/{total_batches}] error: {e} — retrying in {wait:.1f}s", flush=True)
                time.sleep(wait)
                attempt += 1

    print(f"\n✅ Done → {out}")

if __name__ == "__main__":
    main()
