"""
sign_language_comparator.py - Process a CSV of SignPuddle glosses to
analyze handshape usage and generate CSV and Markdown reports.
"""

import sys
import os
import re
import textwrap
import pandas as pd
from collections import defaultdict


def get_country(filename: str) -> tuple[str, str]:
    """
    Verify filename ends with '_sorted_<2 or 4 letters>.csv', extract
    the letter country code, and confirm it in language_codes.csv.

    :param filename: e.g. 'all_ui5_sgn42_fsw_sorted_CHde.csv'
    :return: Tuple (country_code, country_name)
    :raises SystemExit: If file or code invalid.
    """
    # Determine the file’s base name and extension to confirm it’s a CSV
    base = os.path.basename(filename)
    name_no_ext, ext = os.path.splitext(base)

    # Ensure the user provided a CSV file
    if ext.lower() != ".csv":
        print(f"Error: Expected a '.csv' file, but got '{ext}'.")
        sys.exit(1)

    # Check that the filename follows the pattern for country codes
    pattern = r".*_sorted_([A-Za-z]{2}|[A-Za-z]{4})$"
    m = re.match(pattern, name_no_ext, re.IGNORECASE)
    if not m:
        print(
            "Error: File must end in '_sorted_<2 or 4 letters>.csv'."
            f"\nGot: '{base}'"
        )
        sys.exit(1)

    # Extract and normalize the country code
    country_code = m.group(1).upper()

    # Load the mapping of valid codes to country names
    try:
        codes_df = pd.read_csv("language_codes.csv", dtype=str)
    except Exception as e:
        print(f"Error: Could not load 'language_codes.csv': {e}")
        sys.exit(1)

    # Match the extracted code against the list of allowed codes
    codes_df["code_upper"] = codes_df["country_code"].str.upper()
    matches = codes_df[codes_df["code_upper"] == country_code]
    if matches.empty:
        print(
            f"Error: Country code '{country_code}' not found in "
            "language_codes.csv"
        )
        sys.exit(1)

    # Return the valid code and its full country name
    country_name = matches.iloc[0]["country"]
    return country_code, country_name


def check_columns(path: str) -> pd.DataFrame:
    """
    Load the CSV at 'path' and confirm it has dic_gloss, synonyms,
    sid, and FSW.

    :param path: Path to the CSV file.
    :return: DataFrame.
    :raises SystemExit: If file cannot be read or columns missing.
    """
    # Read the CSV into a DataFrame
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Error: Could not read '{path}': {e}")
        sys.exit(1)

    # Ensure all required columns are present before proceeding
    required = {"dic_gloss", "synonyms", "sid", "FSW"}
    missing_col = required - set(df.columns)
    if missing_col:
        print(f"Error: CSV is missing these columns: {', '.join(missing_col)}")
        sys.exit(1)

    return df


def analyze_hs(df: pd.DataFrame, country_code: str, country_name: str) -> None:
    """
    Build u_gloss, extract S1xx codes, count tokens and coverage,
    then write CSV and Markdown reports.

    :param df: DataFrame with required columns.
    :param country_code: Two- or four-letter code.
    :param country_name: Full country name.
    :return: None (writes files).
    """
    print(f"Sign Language Country: {country_name}")

    # Consolidate gloss id fields to create a unique label per entry
    df["u_gloss"] = df.apply(
        lambda row: (
            f"{str(row['dic_gloss']).strip()} "
            f"(sid_{str(row['sid']).strip()})"
            if pd.isna(row["synonyms"]) or str(row["synonyms"]).strip() == ""
            else (
                f"{str(row['dic_gloss']).strip()} "
                f"({str(row['synonyms']).strip()}) "
                f"(sid_{str(row['sid']).strip()})"
            )
        ),
        axis=1
    )

    # Identify all handshape codes (S1xx) embedded in the FSW field
    df["hands"] = df["FSW"].astype(str).apply(
        lambda fsw: re.findall(r"S1[0-9a-f]{2}", fsw)
    )

    # Output a small sample so the user can verify handshape extraction
    print("\nSample of first 50 glosses with extracted handshapes:\n")
    for gloss, hs_list in zip(df["u_gloss"].head(50), df["hands"].head(50)):
        print(f"{gloss}: {hs_list}")

    # Aggregate all extracted handshape tokens into counts
    hs_list = [hs for sub in df["hands"] for hs in sub]
    token_ct = len(hs_list)
    hs_token_ct = pd.Series(hs_list).value_counts()

    # Map each handshape to the set of glosses in which it appears
    hs_gloss_dic = defaultdict(set)
    for gloss, hs_vals in zip(df["u_gloss"], df["hands"]):
        for hs in set(hs_vals):
            hs_gloss_dic[hs].add(gloss)

    # Prepare a table with token counts and gloss coverage per handshape
    gloss_ct = len(df)
    tabular_rows = []
    for hs, hs_t_ct in hs_token_ct.items():
        glosses_per_hs = sorted(hs_gloss_dic[hs])
        hs_gloss_ct = len(glosses_per_hs)
        percent_use = round((hs_t_ct / token_ct) * 100, 2)
        percent_coverage = round((hs_gloss_ct / gloss_ct) * 100, 2)

        tabular_rows.append({
            "Handshape": hs,
            "Token Count": hs_t_ct,
            "% Use": f"{percent_use}%",
            "Gloss Count": hs_gloss_ct,
            "% Gloss Coverage": f"{percent_coverage}%",
            "Glosses Using this Handshape": ", ".join(glosses_per_hs),
        })

    tabular_df = pd.DataFrame(tabular_rows)

    # Add cumulative counts for Pareto-style analysis of handshape usage
    tabular_df["Token Ct (cuml)"] = tabular_df["Token Count"].cumsum()
    tabular_df["Token Ct (cuml%)"] = (
        (tabular_df["Token Ct (cuml)"] / token_ct * 100).round(2)
    )

    # Write the detailed handshape table as a CSV for visual analysis
    code_lower = country_code.lower()
    tabular_csv = f"hs_analysis_{code_lower}.csv"
    tabular_df.to_csv(tabular_csv, index=False)
    print(f"\nCompleted tabular handshape analysis (saved to {tabular_csv})")

    # Identify which glosses lacked any recognizable handshape codes
    empty_df = df[df["hands"].apply(len) == 0]
    g_empty = len(empty_df)

    # Determine the most frequent handshape by token and gloss coverage
    top_hst_i = tabular_df["Token Count"].idxmax()
    top_hst_row = tabular_df.loc[top_hst_i]
    top_hst = top_hst_row["Handshape"]
    top_hst_t_ct = int(top_hst_row["Token Count"])
    top_hst_p = round(top_hst_t_ct / token_ct * 100, 2)
    top_hst_g_ct = int(top_hst_row["Gloss Count"])

    top_hsg_i = tabular_df["Gloss Count"].idxmax()
    top_hsg_row = tabular_df.loc[top_hsg_i]
    top_hsg = top_hsg_row["Handshape"]
    top_hsg_g_ct = int(top_hsg_row["Gloss Count"])
    top_hsg_p = round(top_hsg_g_ct / gloss_ct * 100, 2)

    # Identify how many handshapes account for over 50% of all tokens
    par_i = tabular_df[tabular_df["Token Ct (cuml%)"] > 50].index.min()
    par_hs_ct = par_i + 1
    par_p = round(
        (tabular_df["Token Ct (cuml)"].iloc[par_i] / token_ct) * 100, 2
    )

    # Generate a Markdown report summarizing key findings and exclusions
    report_md = f"hs_report_{code_lower}.md"
    with open(report_md, "w", encoding="utf-8") as doc:
        # Section: Overall summary of handshape statistics
        doc.write("# Handshape Analysis Summary\n\n")
        doc.write("## Overview\n\n")

        overview_text = (
            "The dataset for {c} has a total of {g} glosses in the "
            "SignPuddle Dictionary, of which {hs} contain handshapes "
            "(i.e., include S1xx in their FSW codes). This dataset "
            "contains {t} total handshape tokens, of which {u} are "
            "unique handshapes. The most widely used handshape is "
            "{top_t} with a total of {tt} instances (making up {p}% of "
            "all tokens) over {tg} glosses."
        ).format(
            c=country_name,
            g=gloss_ct,
            hs=(gloss_ct - g_empty),
            t=token_ct,
            u=len(tabular_df),
            top_t=top_hst,
            tt=top_hst_t_ct,
            tg=top_hst_g_ct,
            p=top_hst_p
        )
        doc.write(textwrap.fill(overview_text, width=72) + "\n\n")

        # Section: List of top handshapes by token count
        doc.write("### Handshape Use by Token Count\n\n")
        pareto_text = (
            "A Pareto analysis shows that more than half ({pc}%) of all "
            "handshape tokens correspond to just {p} handshapes in the "
            "dataset. These top {p} are shown below with their token "
            "count, % use, and gloss coverage."
        ).format(p=par_hs_ct, pc=par_p)
        doc.write(textwrap.fill(pareto_text, width=72) + "\n\n")

        par_top = tabular_df.loc[
            :par_i, ["Handshape", "Token Count", "% Use", "Gloss Count"]
        ]
        for i, row in enumerate(par_top.itertuples(index=False), start=1):
            hs = row.Handshape
            t_ct = row[1]
            p_use = row[2]
            g_ct = row[3]
            doc.write(
                f"{i}. **{hs}** ({t_ct} tokens ~ {p_use}, {g_ct} glosses)\n"
            )
        doc.write("\n")

        # Section: List of top handshapes by number of glosses covered
        doc.write("### Handshape Use by Gloss Coverage\n\n")
        gloss_text = (
            "The most used handshape across glosses is {top_g}, appearing "
            "in {g} glosses ({pc}% of all glosses in the dataset). Below "
            "are the top {p} handshapes that cover the most glosses, along "
            "with the number and percent of glosses that include the "
            "handshape at least once."
        ).format(
            top_g=top_hsg,
            g=top_hsg_g_ct,
            pc=top_hsg_p,
            p=par_hs_ct
        )
        doc.write(textwrap.fill(gloss_text, width=72) + "\n\n")

        top_gloss = (
            tabular_df
            .sort_values("Gloss Count", ascending=False)
            .iloc[:par_hs_ct][["Handshape", "Gloss Count", "% Gloss Coverage"]]
        )
        for i, row in enumerate(top_gloss.itertuples(index=False), start=1):
            hs = row.Handshape
            g_ct2 = row[1]
            gc_pct = row[2]
            doc.write(
                f"{i}. **{hs}** ({g_ct2} glosses ~ {gc_pct} of all glosses)\n"
            )
        doc.write("\n")

        # Section: Glosses excluded from handshape frequency analysis
        doc.write("## Exclusions\n\n")
        doc.write("### Glosses Without Handshape\n\n")

        exclusion_text = (
            "Of the {g} total glosses, {p}% ({e} glosses) did not include "
            "any handshape symbol (i.e. no FSW code starting with S1xx) and "
            "thus were excluded from the handshape frequency analysis. "
            "These glosses are listed below."
        ).format(
            g=gloss_ct,
            e=g_empty,
            p=round((g_empty / gloss_ct) * 100, 2)
        )
        doc.write(textwrap.fill(exclusion_text, width=72) + "\n\n")

        for gloss_name, sid_val in zip(empty_df["dic_gloss"], empty_df["sid"]):
            doc.write(f"- {gloss_name} (sid_{sid_val})\n")

    print(f"Created a report summary (saved to {report_md})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sign_language_comparator.py <input_csv>")
        sys.exit(1)

    input_csv = sys.argv[1]
    country_code, country_name = get_country(input_csv)
    print(f"\nCountry code = {country_code}")

    df = check_columns(input_csv)
    analyze_hs(df, country_code, country_name)
