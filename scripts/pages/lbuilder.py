import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)


def load_csv(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def show_columns(columns):
    print("\nAvailable columns:")
    for i, col in enumerate(columns, start=1):
        print(f"{i}. {col}")


def choose_one_column(columns, prompt):
    print(f"\n{prompt}")
    raw = input("> ").strip()
    return columns[int(raw) - 1]


def choose_columns(columns, prompt):
    print(f"\n{prompt}")
    raw = input("> ").strip()
    indices = [int(x.strip()) - 1 for x in raw.split(",")]
    return [columns[i] for i in indices]


def parse_selection(selection, max_index):
    selection = selection.strip().lower()

    if selection == "0":
        return []
    if selection == "all":
        return list(range(max_index))

    chosen = set()

    for part in selection.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start_i = int(start) - 1
            end_i = int(end) - 1
            for i in range(start_i, end_i + 1):
                if 0 <= i < max_index:
                    chosen.add(i)
        else:
            i = int(part) - 1
            if 0 <= i < max_index:
                chosen.add(i)

    return sorted(chosen)


def html_escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_header(column_name):
    return column_name.replace("_", " ").title()


def build_source_label(inventory_row, contributor_column, year_column):
    contributor = inventory_row.get(contributor_column, "").strip() if contributor_column else ""
    year = inventory_row.get(year_column, "").strip() if year_column else ""

    if contributor and year:
        return f"{contributor} ({year})"
    if contributor:
        return contributor
    if year:
        return year
    return ""


def render_language_details(language_row, columns_to_show):
    parts = []
    parts.append("<table border='1' cellspacing='0' cellpadding='6'>")
    parts.append("<tbody>")

    for col in columns_to_show:
        parts.append("<tr>")
        parts.append(f"<th>{html_escape(format_header(col))}</th>")
        parts.append(f"<td>{html_escape(language_row.get(col, ''))}</td>")
        parts.append("</tr>")

    parts.append("</tbody></table>")
    return "\n".join(parts)


def render_inventory_table(
    matching_inventories,
    inventory_id_column,
    inventory_name_column,
    source_label_column,
    ct_segments_column,
):
    if not matching_inventories:
        return ""

    parts = []
    parts.append("<table border='1' cellspacing='0' cellpadding='6'>")
    parts.append("<thead><tr>")
    parts.append("<th>Inventory</th>")
    parts.append("<th>Source</th>")
    parts.append("<th>Segments</th>")
    parts.append("</tr></thead>")
    parts.append("<tbody>")

    for row in matching_inventories:
        inv_id = row.get(inventory_id_column, "")
        inv_name = row.get(inventory_name_column, "")
        source = row.get(source_label_column, "")
        segments = row.get(ct_segments_column, "")
        link = f"../inventories/{inv_id}.html"

        parts.append("<tr>")
        parts.append(f'<td><a href="{html_escape(link)}">{html_escape(inv_name)}</a></td>')
        parts.append(f"<td>{html_escape(source)}</td>")
        parts.append(f"<td>{html_escape(segments)}</td>")
        parts.append("</tr>")

    parts.append("</tbody></table>")
    return "\n".join(parts)


def write_language_page(output_path, title, details_html, inventory_section_html):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_escape(title)}</title>
</head>
<body>
  <h1>{html_escape(title)}</h1>

  <h2>Language Details</h2>
  {details_html}

  <h2>Inventories</h2>
  {inventory_section_html}
</body>
</html>
"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def get_known_defaults(languages_csv, inventories_csv):
    lang_norm = str(Path(languages_csv)).replace("\\", "/").lower()
    inv_norm = str(Path(inventories_csv)).replace("\\", "/").lower()

    if lang_norm.endswith("languages.csv") and inv_norm.endswith("inventories.csv"):
        return {
            "output_folder": "languages",
            "language_id_column": "language_id",
            "language_name_column": "language_name",
            "language_detail_columns": [
                "language_id",
                "language_name",
                "language_abbreviation",
                "glottocode",
                "ISO-639-3",
                "macro-area",
            ],
            "inventory_id_column": "inventory_id",
            "inventory_name_column": "inventory_name",
            "inventory_language_name_column": "language_name",
            "contributor_column": "contributor",
            "year_column": "year",
            "ct_segments_column": "ct_segments",
        }

    return None


def print_discrepancy_report(languages_only, inventories_only):
    print("\n--- Language name cross-check ---")

    if languages_only:
        print("\nIn languages.csv but not found in inventories.csv:")
        for name in languages_only:
            print(f"  - {name}")
    else:
        print("\nAll language names in languages.csv were found in inventories.csv.")

    if inventories_only:
        print("\nIn inventories.csv but not found in languages.csv:")
        for name in inventories_only:
            print(f"  - {name}")
    else:
        print("\nAll inventory language names were found in languages.csv.")


def main():
    print()
    print("This program creates individual language HTML pages from languages.csv.")
    print("Each language page shows the language details and the inventories that match that language.")

    languages_csv = input(
        "\nEnter the path to the languages CSV "
        "(for example: data/slphoible/languages.csv): "
    ).strip()

    inventories_csv = input(
        "Enter the path to the inventories CSV "
        "(for example: data/slphoible/inventories.csv): "
    ).strip()

    languages_rows = load_csv(languages_csv)
    inventories_rows = load_csv(inventories_csv)

    if not languages_rows:
        print("Languages CSV is empty.")
        return
    if not inventories_rows:
        print("Inventories CSV is empty.")
        return

    language_columns = list(languages_rows[0].keys())
    inventory_columns = list(inventories_rows[0].keys())

    defaults = get_known_defaults(languages_csv, inventories_csv)

    if defaults:
        print("\nDetected known CSV files.")
        print(f"Suggested output folder: {defaults['output_folder']}")

        print("\nFrom languages.csv:")
        print(f"  Language ID column: {defaults['language_id_column']}")
        print(f"  Language name column: {defaults['language_name_column']}")
        print("  Language detail columns: " + ", ".join(defaults["language_detail_columns"]))

        print("\nFrom inventories.csv:")
        print(f"  Inventory ID column: {defaults['inventory_id_column']}")
        print(f"  Inventory name column: {defaults['inventory_name_column']}")
        print(f"  Inventory language name column: {defaults['inventory_language_name_column']}")
        print(f"  Contributor column: {defaults['contributor_column']}")
        print(f"  Year column: {defaults['year_column']}")
        print(f"  Count of segments column: {defaults['ct_segments_column']}")

        use_defaults = input("\nUse these defaults? (y/n): ").strip().lower()

        if use_defaults == "y":
            output_folder = defaults["output_folder"]
            language_id_column = defaults["language_id_column"]
            language_name_column = defaults["language_name_column"]
            language_detail_columns = defaults["language_detail_columns"]
            inventory_id_column = defaults["inventory_id_column"]
            inventory_name_column = defaults["inventory_name_column"]
            inventory_language_name_column = defaults["inventory_language_name_column"]
            contributor_column = defaults["contributor_column"]
            year_column = defaults["year_column"]
            ct_segments_column = defaults["ct_segments_column"]
        else:
            output_folder = input(
                "\nEnter the output folder for the language pages "
                "(for example: languages): "
            ).strip()

            print("\n--- languages.csv columns ---")
            show_columns(language_columns)
            language_id_column = choose_one_column(language_columns, "Select the language ID column from languages.csv")
            language_name_column = choose_one_column(language_columns, "Select the language name column from languages.csv")
            language_detail_columns = choose_columns(
                language_columns,
                "Enter the column numbers to show in the language details table, separated by commas:"
            )

            print("\n--- inventories.csv columns ---")
            show_columns(inventory_columns)
            inventory_id_column = choose_one_column(inventory_columns, "Select the inventory ID column from inventories.csv")
            inventory_name_column = choose_one_column(inventory_columns, "Select the inventory name column from inventories.csv")
            inventory_language_name_column = choose_one_column(
                inventory_columns,
                "Select the language name column from inventories.csv (used for matching):"
            )
            contributor_column = choose_one_column(inventory_columns, "Select the contributor column from inventories.csv")
            year_column = choose_one_column(inventory_columns, "Select the year column from inventories.csv")
            ct_segments_column = choose_one_column(inventory_columns, "Select the count of segments column from inventories.csv")
    else:
        output_folder = input(
            "\nEnter the output folder for the language pages "
            "(for example: languages): "
        ).strip()

        print("\n--- languages.csv columns ---")
        show_columns(language_columns)
        language_id_column = choose_one_column(language_columns, "Select the language ID column from languages.csv")
        language_name_column = choose_one_column(language_columns, "Select the language name column from languages.csv")
        language_detail_columns = choose_columns(
            language_columns,
            "Enter the column numbers to show in the language details table, separated by commas:"
        )

        print("\n--- inventories.csv columns ---")
        show_columns(inventory_columns)
        inventory_id_column = choose_one_column(inventory_columns, "Select the inventory ID column from inventories.csv")
        inventory_name_column = choose_one_column(inventory_columns, "Select the inventory name column from inventories.csv")
        inventory_language_name_column = choose_one_column(
            inventory_columns,
            "Select the language name column from inventories.csv (used for matching):"
        )
        contributor_column = choose_one_column(inventory_columns, "Select the contributor column from inventories.csv")
        year_column = choose_one_column(inventory_columns, "Select the year column from inventories.csv")
        ct_segments_column = choose_one_column(inventory_columns, "Select the count of segments column from inventories.csv")

    valid_languages = [
        row for row in languages_rows
        if row.get(language_id_column, "").strip().startswith("lan")
    ]

    valid_inventories = [
        row for row in inventories_rows
        if row.get(inventory_id_column, "").strip().startswith("inv")
    ]

    if not valid_languages:
        print("No valid language rows found.")
        return
    if not valid_inventories:
        print("No valid inventory rows found.")
        return

    for inv in valid_inventories:
        inv["_source_label_temp"] = build_source_label(inv, contributor_column, year_column)

    language_names = {
        row.get(language_name_column, "").strip()
        for row in valid_languages
        if row.get(language_name_column, "").strip()
    }

    inventory_language_names = {
        row.get(inventory_language_name_column, "").strip()
        for row in valid_inventories
        if row.get(inventory_language_name_column, "").strip()
    }

    languages_only = sorted(language_names - inventory_language_names)
    inventories_only = sorted(inventory_language_names - language_names)

    print_discrepancy_report(languages_only, inventories_only)

    continue_anyway = input(
        "\nContinue with exact language-name matching anyway? (y/n): "
    ).strip().lower()

    if continue_anyway != "y":
        print("Cancelled.")
        return

    print("\n--- Valid languages ---")
    for i, row in enumerate(valid_languages, start=1):
        print(f"{i}. {row.get(language_id_column, '')} | {row.get(language_name_column, '')}")

    print("\nChoose language pages to build:")
    print("  all = all valid languages")
    print("  0   = none")
    print("  1-5 = range")
    print("  1,4,7 = specific entries")
    selection = input("> ").strip().lower()

    chosen_indexes = parse_selection(selection, len(valid_languages))
    selected_languages = [valid_languages[i] for i in chosen_indexes]

    if not selected_languages:
        print("No languages selected.")
        return

    generated = 0

    for language_row in selected_languages:
        language_id = language_row.get(language_id_column, "").strip()
        language_name = language_row.get(language_name_column, "").strip()

        matching_inventories = [
            inv for inv in valid_inventories
            if inv.get(inventory_language_name_column, "").strip() == language_name
        ]

        details_html = render_language_details(language_row, language_detail_columns)

        if matching_inventories:
            inventory_section_html = render_inventory_table(
                matching_inventories,
                inventory_id_column=inventory_id_column,
                inventory_name_column=inventory_name_column,
                source_label_column="_source_label_temp",
                ct_segments_column=ct_segments_column,
            )
        else:
            inventory_section_html = f"<p>No inventories found for {html_escape(language_name)}.</p>"

        title = f"{language_name}"
        output_path = Path(output_folder) / f"{language_id}.html"
        write_language_page(output_path, title, details_html, inventory_section_html)
        generated += 1

    print(f"\nCreated {generated} language page(s) in: {output_folder}")


if __name__ == "__main__":
    main()
