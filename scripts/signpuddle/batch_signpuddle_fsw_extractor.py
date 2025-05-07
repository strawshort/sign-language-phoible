import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, quote_plus
import pandas as pd

# ——— CONFIG —————————————————————————————————————————————————————————
BASE       = 'https://www.signbank.org/signpuddle2.0/'
UI, SGN    = 5, 55               # change these per language/dictionary
OUTPUT     = f"all_ui{UI}_sgn{SGN}_fsw.csv"
BATCH_SIZE = 100                 # how many SIDs per HTTP request

# ——— 1) grab the master SID list from the “Print Puddle” link ——————————————————
idx_url = f"{BASE}searchword.php?ui={UI}&sgn={SGN}&sTrm=*"
r = requests.get(idx_url); r.raise_for_status()
idx_soup = BeautifulSoup(r.text, 'html.parser')
print_link = idx_soup.find('a', href=lambda h: h and 'print?puddle=sgn' in h)
ids_param  = parse_qs(urlparse(print_link['href']).query)['ids'][0].split(',')

# ——— 2) break into batches —————————————————————————————————————————————
batches = [
    ids_param[i:i+BATCH_SIZE]
    for i in range(0, len(ids_param), BATCH_SIZE)
]

# ——— 3) remove old output if present ————————————————————————————————————
if os.path.exists(OUTPUT):
    os.remove(OUTPUT)

# ——— 4) loop over each batch and append to one CSV ——————————————————————
for batch_idx, batch in enumerate(batches, start=1):
    sid_list = quote_plus(','.join(batch))
    url = (
        f"{BASE}searchword.php?"
        f"ui={UI}&sgn={SGN}"
        f"&sid={sid_list}&sTrm=*"
    )
    print(f"[{batch_idx}/{len(batches)}] Fetching {len(batch)} sids…")
    page = BeautifulSoup(requests.get(url).text, 'html.parser')

    rows = []
    for tbl in page.find_all('table', attrs={'cellpadding':'10'}):
        cell      = tbl.find('td')
        canonical = cell.find('font', size='+1').get_text(strip=True)
        parts     = cell.get_text("||", strip=True).split("||")
        synonyms  = parts[1] if len(parts)>1 else ''

        small = tbl.find_next('small')

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

    # append this batch’s rows to the CSV
    df = pd.DataFrame(rows)
    df.to_csv(
        OUTPUT,
        mode='a',
        header=(batch_idx == 1),  # write header only once
        index=False
    )

print(f"\n✅ All done! Combined CSV: {OUTPUT}")
