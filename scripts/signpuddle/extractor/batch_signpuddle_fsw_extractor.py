import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, quote_plus
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

__version__ = "1.1.1"

# ——— CONFIG —————————————————————————————————————————————————————————
BASE       = 'https://www.signbank.org/signpuddle2.0/'
UI, SGN    = 5, 55               # change these per language/dictionary
OUTPUT     = f"all_ui{UI}_sgn{SGN}_fsw_ES.csv"
BATCH_SIZE = 500                 # how many SIDs per HTTP request
MAX_WORKERS = 8                  # number of parallel threads

# ——— 1) grab the master SID list (bulk or per-gloss fallback) ——————————————————
idx_url    = f"{BASE}searchword.php?ui={UI}&sgn={SGN}&sTrm=*"
sess       = requests.Session()
r          = sess.get(idx_url)
r.raise_for_status()
idx_soup   = BeautifulSoup(r.text, 'lxml')  # faster parser

print_link = idx_soup.find('a', href=lambda h: h and 'print?puddle=sgn' in h)
if print_link is not None:
    ids_param = (
        parse_qs(urlparse(print_link['href']).query)['ids'][0].split(',')
    )
else:
    print("⚠️  No bulk-SID link; scraping gloss links individually…")
    seen = set()
    for a in idx_soup.find_all('a', href=lambda h: h and 'searchword.php' in h and 'sid=' in h):
        raw = parse_qs(urlparse(a['href']).query).get('sid', [''])[0]
        for sid in raw.split(','):
            if sid:
                seen.add(sid)
    ids_param = list(seen)

# ——— 2) break into batches —————————————————————————————————————————————
batches = [ids_param[i:i+BATCH_SIZE] for i in range(0, len(ids_param), BATCH_SIZE)]

# ——— 3) remove old output if present ————————————————————————————————————
if os.path.exists(OUTPUT):
    os.remove(OUTPUT)

# ——— helper: fetch one batch ——————————————————————————————————————
def fetch_batch(batch):
    sid_list = quote_plus(','.join(batch))
    url = f"{BASE}searchword.php?ui={UI}&sgn={SGN}&sid={sid_list}&sTrm=*"
    page = BeautifulSoup(sess.get(url).text, 'lxml')
    rows = []
    for tbl in page.find_all('table', attrs={'cellpadding':'10'}):
        cell      = tbl.find('td')
        canonical = cell.find('font', size='+1').get_text(strip=True)
        parts     = cell.get_text("||", strip=True).split("||")
        synonyms  = parts[1] if len(parts)>1 else ''
        small     = tbl.find_next('small')
        # extract FSW
        fsw = None
        for span in small.find_all('span'):
            prev = span.find_previous(string=True) or ""
            if 'FSW:' in prev:
                fsw = span.get_text(strip=True)
                break
        # extract SID
        puddle = small.find('a', href=lambda h: h and 'canvas.php' in h)
        sid    = parse_qs(urlparse(puddle['href']).query)['sid'][0]
        rows.append({
            'canonical_gloss': canonical,
            'synonyms':        synonyms,
            'sid':             sid,
            'FSW':             fsw
        })
    return rows

# ——— 4) parallel fetch, write CSV ————————————————————————————————————
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    for batch_idx, rows in enumerate(executor.map(fetch_batch, batches), start=1):
        print(f"[{batch_idx}/{len(batches)}] Fetched {len(rows)} rows…")
        df = pd.DataFrame(rows)
        df.to_csv(
            OUTPUT,
            mode='a',
            header=(batch_idx == 1),
            index=False
        )

print(f"\n✅ All done! Combined CSV: {OUTPUT}")
