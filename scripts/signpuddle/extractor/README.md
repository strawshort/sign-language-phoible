# SignPuddle FSW Extractor

This script pulls **all** sign entries from a given SignPuddle dictionary and extracts the following fields. 
Each entry refers to an individual sign detail page (accessed via its unique SID), 
which may display a primary term and synonyms that differ from the original search term in the index.

* **canonical\_gloss**: the primary term displayed on the entry’s table
* **synonyms**: any additional synonyms listed below the primary term (comma-separated)
* **sid**: the unique SignPuddle ID for the dictionary entry
* **FSW**: the Family SignWriting code


## Prerequisites

Install dependencies with:

```bash
pip install -r requirements.txt
```

The main dependencies are:
* pandas
* requests
* beautifulsoup4
* tqdm
* lxml (used by BeautifulSoup for parsing HTML)

*Note:* Missing `lxml` will raise a `Couldn't find a tree builder` error.

## Configuration

At the top of the script (under CONFIG), set the following parameters:

```python
# ——— CONFIG ————————————————————————————————————————————————
BASE        = 'https://www.signbank.org/signpuddle2.0/'
UI, SGN     = 5, 55               # change these per language/dictionary
OUTPUT      = f"all_ui{UI}_sgn{SGN}_fsw_ES.csv"
BATCH_SIZE  = 500                 # entries per request
MAX_WORKERS = 8                   # parallel requests
```

Modify the values for target language and dictionary:
- `UI` interface language code (e.g. 5 = Spanish)
- `SGN` = 55 dictionary ID (e.g. 55 = España, LSE)
- These are listed in `signpuddle_language_codes.csv` or dictionary URLs (e.g. *ui=5&sgn=55*)

Modify the country code in the `OUTPUT` filename:
- Use codes (omitting dashes) from `signpuddle_language_codes.csv`
- Example (ES) `all_ui5_sgn55_fsw_ES.csv`
- Example (CH-de) `all_ui8_sgn48_fsw_CHde.csv`
- This is used downstream as input into the Sign Language Comparator script

(Optional) Change how fast the script runs by adjusting:
- `BATCH_SIZE` how many entries (SIDs) are downloaded per HTTP request
- `MAX_WORKERS` how many batch requests are executed in parallel
- The script iterates through SIDs in sequential batches until all entries are retrieved.



## Usage

After installing the required packages, run:

```bash
python batch_signpuddle_fsw_extractor.py
```

The script:
  1. Retrieves FSW entries in batches.
  2. Combines them into a single output CSV.
  3. Displays a progress bar for each batch.
  4. Confirms completion and lists the output file.

Example output:
```python
[1/7] Fetched 500 rows…
[2/7] Fetched 500 rows…
[7/7] Fetched 465 rows…
✅ All done! Combined CSV: all_ui8_sgn48_fsw_CHde.csv
```


## Output

The script writes a single CSV file named:

```
all_ui{UI}_sgn{SGN}_fsw_CC.csv
```
where CC would be the Country Code.


For example, with the default settings it outputs:

```
all_ui5_sgn55_fsw_ES.csv
```

Each CSV row represents one SignPuddle entry with its gloss, synonyms, SID, and FSW code.
