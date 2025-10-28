# SignPuddle FSW Extractor

## Description

Extracts all Formal SignWriting (FSW) entries of a selected dictionary from SignPuddle Online and saves them to a CSV with the following columns:

| Column | Description |
|------|--------------|
|`canonical_gloss`| The main term displayed on the entry's page
|`synonyms`| Additional terms that redirect to the same entry (comma-separated)
|`sid`| The unique SignPuddle ID for the main entry
|`FSW`| The Family SignWriting code string

<br>

Each SignPuddle dictionary includes main entries with a unique Sign ID and synonyms that link to those entries. (For example, in the Hong Kong dictionary, *profession* redirects to *subject* (SID 4), where *subject* is the `canonical gloss` and *profession* is the `synonym`.) The extractor identifies each entry by its unique `SID` and records its canonical gloss along with its FSW string and any linked synonyms.
This keeps related terms grouped under a single entry and prevents duplicates in the CSV.


## Features

- **Guided Prompting** – Lists dictionary options, auto-sets parameters, summarizes entries, and confirms extraction.

- **Large dictionary handling** – Retrieves entries in batches with built-in pacing and retry handling.

- **Progress visibility** – Prints clear updates for each batch and total progress.


## Prerequisites

```bash
pip install -r requirements.txt
```

The main dependencies are:
- `pandas`
- `requests`
- `beautifulsoup4`
- `lxml`

*Note:* Without `lxml`. Beautifulsoup will raise a `Couldn't find a tree builder` error.

## Usage

1. **Run the script:**

```bash
python batch_signpuddle_fsw_extractor.py
```

- Example Output:

```
SignPuddle FSW Extractor v2.0.0
Extracts FSW entries from SignPuddle for a selected dictionary and writes a CSV.

Available SignPuddle Language Options
 country_code  country              ui  sgn
 AF                  Afghanistan          1  106
 AL                  Albania              1  82
 AR                  Argentina            5  41
 ...
 DE                  Deutschland, Germany 8  53
 ...

Enter country code: 
```

2. **Select and review:** *Choose a country code, review SID total, and confirm to proceed.* 

- Example Output (without bulk-SID):

```
...
Enter country code: DE

Using Deutschland, Germany (DE) → ui=8, sgn=53
Output: all_ui8_sgn53_fsw_DE.csv

Fetching index page for Deutschland, Germany ...
⏳ Waiting for server response (up to 60s before next attempt)

⚠️  No bulk-SID link found.
📋 Found 24,702 SIDs by scanning index page.

Proceed with fetching all 24,702 entries? (y/n):
```
- Example Output  (with bulk-SID):

```
...
Enter country code: US

Using USA (US) → ui=1, sgn=4
Output: all_ui1_sgn4_fsw_US.csv

Fetching index page for USA ...
⏳ Waiting for server response (up to 60s before next attempt)

✅ Found bulk-SID link. Counting entries...
📋 Total: 11,984 entries.

Proceed with fetching all 11,984 entries? (y/n):
```

3. **Proceed:** The tool writes a single CSV combining all entries. *Request timeouts are automatically retried.*
```
Proceed with fetching all 24,702 entries? (y/n): y

Found 24,702 SIDs. Fetching in 3 batch(es) of 10000…

[1/3] 10000 rows
[2/3] 10000 rows
[3/3] error: HTTPSConnectionPool(host='www.signbank.org', port=443): Read timed out. — retrying in 0.5s
[3/3] 4702 rows

✅ Done → all_ui8_sgn53_fsw_DE.csv
```

4. **Abort:** Option to skip a large dataset with long runtime


```
...
Proceed with fetching all 154 entries? (y/n): n
Aborted by user.
```

###Optional Arguments

| Flag | Description |
|------|--------------|
| `--cc` | Specify country code directly (e.g., `--cc=DE`) |
| `--batch-size` | Set custom batch size (default: 10000) |
| `--version` | Show script version |

Example non-interactive run:
```bash
python3 batch_signpuddle_fsw_extractor.py --cc=US --batch-size=5000
```

### Output

The script generates a CSV file named:

```
all_ui<UI>_sgn<SGN>_fsw_<COUNTRY>.csv
```

Example:

```
all_ui8_sgn53_fsw_DE.csv
```

## Version

`batch_signpuddle_fsw_extractor.py` – v2.0.0  
Last updated: October 2025