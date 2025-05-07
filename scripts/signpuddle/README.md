# SignPuddle FSW Extractor

This script pulls **all** sign entries from a given SignPuddle dictionary and extracts the following fields. Each entry refers to an individual sign detail page (accessed via its unique SID), which may display a primary term and synonyms that differ from the original search term in the index.

* **canonical\_gloss**: the primary term displayed on the entry’s table
* **synonyms**: any additional synonyms listed below the primary term (comma-separated)
* **sid**: the unique SignPuddle ID for the dictionary entry
* **FSW**: the Family SignWriting code


## Prerequisites

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Configuration

At the top of the script (under CONFIG), adjust the following variables:

* To target a different dictionary or language, modify `UI` and `SGN`.
* To change how many SIDs are fetched per request, adjust `BATCH_SIZE`.

```python
UI         = 5       # interface language code (e.g. 5 = Spanish)
SGN        = 55      # dictionary ID (e.g. 55 = España, LSE)
BATCH_SIZE = 100     # number of SIDs to fetch per HTTP request
```
* The `UI` and `SGN` values are indicated in the URL of the corresponding SignPuddle dictionary (e.g. ui=5&sgn=55).
* `BATCH_SIZE` controls the number of entries per HTTP call, so that script will iterate in batches through all available SIDs until completion.

## Usage

```bash
python batch_signpuddle_fsw_extractor.py
```

## Output

The script writes a single CSV file named:

```
all_ui{UI}_sgn{SGN}_fsw.csv
```

For example, with the default settings it outputs:

```
all_ui5_sgn55_fsw.csv
```
