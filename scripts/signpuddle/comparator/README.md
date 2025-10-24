# Sign Language Comparator

## Overview

Sign Language Comparator is a Python command-line script that processes a CSV of SignPuddle glosses to analyze handshape usage and automatically produce a CSV detailing handshape frequencies and coverage, along with a comprehensive Markdown report that summarizes the analysis for that language. It validates the country code from the filename against a reference list, extracts handshape tokens from FSW codes, computes frequency and coverage statistics, and produces detailed reports for further analysis.

This tool supports phonological research by identifying which handshapes are most frequent and how they distribute across the lexicon of a single sign language. By analyzing a SignPuddle CSV export—where each entry includes a gloss (with optional synonyms) and an FSW string—researchers can see dominant handshape patterns, coverage percentages, and gloss similarities, helping to reveal structural trends within the language.

## Features

* **Country Code Validation:** Verifies that the input CSV filename ends with `_sorted_<2 or 4 letters>.csv` and confirms the code against `language_codes.csv`.
* **Column Integrity Check:** Ensures the required columns (`dic_gloss`, `synonyms`, `sid`, `FSW`) are present and exits with an error if any are missing.
* **Handshape Extraction:** Parses FSW codes to extract all `S1xx` handshape tokens.
* **Sample Preview:** Prints the first 50 glosses with their extracted handshapes to the console for quick inspection.
* **Frequency Analysis:** Counts total handshape tokens, computes token and gloss coverage percentages, and organizes results into a tabular DataFrame.
* **CSV Report Generation:** Saves a detailed handshape analysis table (`hs_analysis_<country_code>.csv`) containing token counts, cumulative counts, coverage percentages, and gloss lists.

  * **Note:** The cumulative count columns are included at the end of the CSV for reference, so as not to distract from the primary statistics.
* **Markdown Summary:** Writes a comprehensive summary report (`hs_report_<country_code>.md`) that includes:

  * Overview statistics of glosses and handshape tokens
  * Pareto analysis of top handshapes by token count
  * Top handshapes by gloss coverage
  * Identification of glosses without any handshape codes

## Installation

### Requirements

* **Python 3.x** (Tested with Python 3.8 and above)

* **pandas** (Tested with pandas 1.5.0)

  Install pandas via pip:

  ```bash
  pip install pandas
  ```

* **language\_codes.csv** in the same directory, containing two columns:

  * `country_code` (e.g., `CHde`, `AR`, etc.)
  * `country` (e.g., `German Switzerland`, `Argentina`, etc.)

### Setup

1. **Clone or copy** `sign_language_comparator.py` into your working directory.
2. **Ensure** that `language_codes.csv` is present in the same folder.
3. **Prepare** your input CSV file named in the format:

   ```
   <any_prefix>_sorted_<2 or 4 letters>.csv
   ```

   For example: `all_ui5_sgn42_fsw_sorted_CHde.csv`

## Usage

### Command Syntax

```bash
python sign_language_comparator.py <input_csv>
```

### Arguments

* `<input_csv>`
  Path to the input CSV file. Must end with `_sorted_<2 or 4 letters>.csv`.

### Example Commands

1. **Basic execution**:
   Validate country code, analyze handshapes, and generate reports.

   ```bash
   python sign_language_comparator.py all_ui5_sgn42_fsw_sorted_CHde.csv
   ```

2. **Sample output**:
   After running, you will see:

   ```text
   Country code = CHDE
   Sign Language Country: German Switzerland

   Sample of first 50 glosses with extracted handshapes:
   gloss1 (sid_123): ['S101', 'S10a']
   gloss2 (sid_456): ['S1f2']
   ...
   Completed tabular handshape analysis (saved to hs_analysis_chde.csv)
   Created a report summary (saved to hs_report_chde.md)
   ```

## Notes

* Data cleaning of gloss text is not done prior to processing because filtering by `S1xx` handshape codes inherently excludes non-handshape entries. Attempting to clean gloss strings beforehand could remove important annotations (e.g., forms marked with `?1`, `?2`, or compound markers), and annotation conventions vary by country. By relying on FSW analysis for handshape extraction, the script preserves all meaningful information.

## License

**Academic Assignment Disclaimer:**
This code was developed for a class or research project and is not licensed for redistribution or commercial use without permission. If you wish to reuse or modify this code, please contact the author.

## References

SignPuddle Online: https://www.signbank.org/signpuddle/

ISWA 2010 (International SignWriting Alphabet): https://www.signbank.org/iswa/

## Contact

For questions or feedback, contact Luz Diaz Hernández at [luzelenia.diazhernandez@uzh.ch](mailto:luzelenia.diazhernandez@uzh.ch).
