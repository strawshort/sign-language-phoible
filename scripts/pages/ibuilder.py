import csv
import html
from pathlib import Path
import sys

csv.field_size_limit(sys.maxsize)

SIGNWRITING_FONT_CSS = """
<style>
@font-face {
  font-family: "SuttonSignWritingLine";
  src:
    local('SuttonSignWritingLine'),
    url('https://unpkg.com/@sutton-signwriting/font-ttf@1.0.0/font/SuttonSignWritingLine.ttf') format('truetype');
}
@font-face {
  font-family: "SuttonSignWritingFill";
  src:
    local('SuttonSignWritingFill'),
    url('https://unpkg.com/@sutton-signwriting/font-ttf@1.0.0/font/SuttonSignWritingFill.ttf') format('truetype');
}
@font-face {
  font-family: "SuttonSignWritingOneD";
  src:
    local('SuttonSignWritingOneD'),
    url('https://unpkg.com/@sutton-signwriting/font-ttf@1.0.0/font/SuttonSignWritingOneD.ttf') format('truetype');
}
.signwriting {
  font-family: "SuttonSignWritingOneD", "SuttonSignWritingLine", "SuttonSignWritingFill";
  font-size: 2em;
}
</style>
"""

def load_csv(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def show_columns(columns):
    print("\nAvailable columns:")
    for i, col in enumerate(columns, start=1):
        print(f"{i}. {col}")


def choose_columns(columns, prompt, allow_none=False):
    print(f"\n{prompt}")
    if allow_none:
        print("Enter column numbers separated by commas, or 0 for none.")
    else:
        print("Enter column numbers separated by commas.")

    raw = input("> ").strip()

    if allow_none and raw == "0":
        return []

    indices = [int(x.strip()) - 1 for x in raw.split(",")]
    return [columns[i] for i in indices]


def choose_one_column(columns, prompt):
    print(f"\n{prompt}")
    raw = input("> ").strip()
    return columns[int(raw) - 1]


def find_matching_file(folder, source_code):
    folder_path = Path(folder)
    matches = list(folder_path.glob(f"{source_code}_*.csv"))
    if not matches:
        return None
    return matches[0]


def build_segments_lookup(segments_rows, fsw_column, segment_id_column):
    lookup = {}
    for row in segments_rows:
        fsw = row.get(fsw_column, "").strip()
        if fsw:
            lookup[fsw] = dict(row)
            lookup[fsw]["segment_id"] = row.get(segment_id_column, "").strip()
    return lookup


def join_inventory_rows(source_rows, source_fsw_column, segments_lookup, segment_columns_to_add):
    joined = []
    for row in source_rows:
        fsw_value = row.get(source_fsw_column, "").strip()
        segment_row = segments_lookup.get(fsw_value, {})

        new_row = {"segment_id": segment_row.get("segment_id", "")}

        for col in segment_columns_to_add:
            new_row[col] = segment_row.get(col, "")

        joined.append(new_row)

    return joined


def build_fsw_link(fsw_value, segment_id):
    if not segment_id:
        return html.escape(fsw_value)
    href = f"../segments/{segment_id}.html"
    return f'<a href="{html.escape(href)}">{html.escape(fsw_value)}</a>'


def format_header(column_name):
    return column_name.replace("_", " ").title()


def render_table(rows, columns_to_show, fsw_column):
    parts = []
    parts.append("<table border='1' cellspacing='0' cellpadding='6'>")
    parts.append("<thead><tr>")

    for col in columns_to_show:
        parts.append(f"<th>{html.escape(format_header(col))}</th>")

    parts.append("</tr></thead>")
    parts.append("<tbody>")

    for row in rows:
        parts.append("<tr>")
        for col in columns_to_show:
            value = row.get(col, "")
            if col == fsw_column:
                cell = build_fsw_link(value, row.get("segment_id", ""))
            else:
                cell = html.escape(value)

            if col.startswith("signwriting"):
                parts.append(f'<td class="signwriting">{cell}</td>')
            else:
                parts.append(f"<td>{cell}</td>")
        parts.append("</tr>")

    parts.append("</tbody></table>")
    return "\n".join(parts)


def render_inventory_metadata(inventory_row):
    wanted = [
        "inventory_id",
        "inventory_name",
        "language_name",
        "data_source",
        "contributor",
        "cite",
    ]

    parts = []
    parts.append("<table border='1' cellspacing='0' cellpadding='6'>")
    parts.append("<tbody>")

    for key in wanted:
        if key in inventory_row:
            parts.append("<tr>")
            parts.append(f"<th>{html.escape(format_header(key))}</th>")
            parts.append(f"<td>{html.escape(inventory_row.get(key, ''))}</td>")
            parts.append("</tr>")

    parts.append("</tbody></table>")
    return "\n".join(parts)


def write_inventory_page(output_path, title, metadata_html, table_html):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  {SIGNWRITING_FONT_CSS}
</head>
<body>
  <h1>{html.escape(title)}</h1>

  <h2>Inventory Details</h2>
  {metadata_html}

  <h2>Segments</h2>
  {table_html}
</body>
</html>
"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def get_source_family(source_code):
    return source_code.split("_")[0].strip()


def get_known_defaults(inventories_csv, segments_csv):
    inv_name = Path(inventories_csv).name
    seg_name = Path(segments_csv).name

    if (
        inv_name.startswith("inventories") and Path(inventories_csv).suffix == ".csv"
        and seg_name.startswith("segments") and Path(segments_csv).suffix == ".csv"
    ):
        return {
            "output_folder": "inventories",
            "segment_id_column": "segment_id",
            "segment_fsw_column": "fsw",
            "segment_columns_to_add": [
                "segment_class",
                "hamnosys_1_initial_configuration",
                "hamnosys_2_basic_handshape",
                "hamnosys_3_handshape_modifications",
                "fsw",
                "signwriting_1",
                "signwriting_2",
            ],
            "source_file_column": "data_source",
            "source_folder_column": "data_source_location",
            "inventory_id_column": "inventory_id",
            "inventory_title_column": "inventory_name",
        }

    return None


def collect_missing_fsws(valid_inventories, source_file_column, source_folder_column, family_configs, segments_lookup):
    missing_fsws = set()

    for inv in valid_inventories:
        source_code = inv[source_file_column].strip()
        family = get_source_family(source_code)

        if family not in family_configs:
            continue

        source_file = find_matching_file(
            inv[source_folder_column],
            inv[source_file_column],
        )

        if not source_file:
            continue

        source_rows = load_csv(source_file)
        source_fsw_column = family_configs[family]["source_fsw_column"]

        for row in source_rows:
            fsw_value = row.get(source_fsw_column, "").strip()
            if fsw_value and fsw_value not in segments_lookup:
                missing_fsws.add(fsw_value)

    return sorted(missing_fsws)


def main():
    print()
    print("This program creates individual inventory HTML pages from inventories.csv.")
    print("It displays the inventory details, reads the FSW values from each inventory source file, and uses segments.csv to show the corresponding standardized segment information.")

    inventories_csv = input(
        "\nEnter the path to the inventories CSV "
        "(for example: data/slphoible/inventories.csv): "
    ).strip()

    segments_csv = input(
        "Enter the path to the segments CSV "
        "(for example: data/slphoible/segments.csv): "
    ).strip()

    inventories_rows = load_csv(inventories_csv)
    segments_rows = load_csv(segments_csv)

    if not inventories_rows:
        print("Inventories CSV is empty.")
        return
    if not segments_rows:
        print("Segments CSV is empty.")
        return

    segments_columns = list(segments_rows[0].keys())
    inventories_columns = list(inventories_rows[0].keys())

    defaults = get_known_defaults(inventories_csv, segments_csv)

    if defaults:
        print("\nDetected known CSV files.")
        print(f"Suggested output folder: {defaults['output_folder']}")

        print("\nFrom segments.csv:")
        print(f"  Segment ID column: {defaults['segment_id_column']}")
        print(f"  FSW column: {defaults['segment_fsw_column']}")
        print("  Segment columns to add: " + ", ".join(defaults["segment_columns_to_add"]))

        print("\nFrom inventories.csv:")
        print(f"  Data source column: {defaults['source_file_column']}")
        print(f"  Data source location column: {defaults['source_folder_column']}")
        print(f"  Inventory ID column: {defaults['inventory_id_column']}")
        print(f"  Inventory name column: {defaults['inventory_title_column']}")

        use_defaults = input("\nUse these defaults? (y/n): ").strip().lower()

        if use_defaults == "y":
            output_folder = defaults["output_folder"]
            segment_id_column = defaults["segment_id_column"]
            segment_fsw_column = defaults["segment_fsw_column"]
            segment_columns_to_add = defaults["segment_columns_to_add"]
            source_file_column = defaults["source_file_column"]
            source_folder_column = defaults["source_folder_column"]
            inventory_id_column = defaults["inventory_id_column"]
            inventory_title_column = defaults["inventory_title_column"]
        else:
            output_folder = input(
                "\nEnter the output folder for the inventory pages "
                "(for example: inventories): "
            ).strip()

            print("\n--- segments.csv columns ---")
            show_columns(segments_columns)
            segment_id_column = choose_one_column(segments_columns, "Select the segment ID column from segments.csv")
            segment_fsw_column = choose_one_column(segments_columns, "Select the FSW column from segments.csv")
            segment_columns_to_add = choose_columns(
                segments_columns,
                "Select the columns from segments.csv to include on all inventory pages",
                allow_none=True,
            )

            print("\n--- inventories.csv columns ---")
            show_columns(inventories_columns)
            source_file_column = choose_one_column(inventories_columns, "Select the data source column from inventories.csv")
            source_folder_column = choose_one_column(inventories_columns, "Select the source folder column from inventories.csv")
            inventory_id_column = choose_one_column(inventories_columns, "Select the inventory ID column from inventories.csv")
            inventory_title_column = choose_one_column(inventories_columns, "Select the inventory name column from inventories.csv")
    else:
        output_folder = input(
            "\nEnter the output folder for the inventory pages "
            "(for example: inventories): "
        ).strip()

        print("\n--- segments.csv columns ---")
        show_columns(segments_columns)
        segment_id_column = choose_one_column(segments_columns, "Select the segment ID column from segments.csv")
        segment_fsw_column = choose_one_column(segments_columns, "Select the FSW column from segments.csv")
        segment_columns_to_add = choose_columns(
            segments_columns,
            "Select the columns from segments.csv to include on all inventory pages",
            allow_none=True,
        )

        print("\n--- inventories.csv columns ---")
        show_columns(inventories_columns)
        source_file_column = choose_one_column(inventories_columns, "Select the data source column from inventories.csv")
        source_folder_column = choose_one_column(inventories_columns, "Select the source folder column from inventories.csv")
        inventory_id_column = choose_one_column(inventories_columns, "Select the inventory ID column from inventories.csv")
        inventory_title_column = choose_one_column(inventories_columns, "Select the inventory name column from inventories.csv")

    page_count_input = input(
        "\nHow many inventory pages do you want to generate? Enter a number or 'all': "
    ).strip().lower()

    if segment_id_column in segment_columns_to_add:
        segment_columns_to_add = [
            col for col in segment_columns_to_add
            if col != segment_id_column
        ]

    valid_inventories = [
        row for row in inventories_rows
        if row.get(inventory_id_column, "").strip().startswith("inv")
    ]

    if not valid_inventories:
        print("No valid inventory rows found.")
        return

    if page_count_input != "all":
        page_count = int(page_count_input)
        valid_inventories = valid_inventories[:page_count]

    family_configs = {}

    for inv in valid_inventories:
        source_code = inv[source_file_column].strip()
        family = get_source_family(source_code)

        if family in family_configs:
            continue

        sample_file = find_matching_file(
            inv[source_folder_column],
            inv[source_file_column],
        )

        if not sample_file:
            print(f"Skipping source family {family}: no matching sample file found.")
            continue

        sample_rows = load_csv(sample_file)
        if not sample_rows:
            print(f"Skipping source family {family}: sample file is empty.")
            continue

        source_columns = list(sample_rows[0].keys())

        print(f"\n--- Source family: {family} ---")
        show_columns(source_columns)

        source_fsw_column = choose_one_column(
            source_columns,
            f"Select the FSW column for all {family} source files",
        )

        family_configs[family] = {
            "source_fsw_column": source_fsw_column,
        }

    segments_lookup = build_segments_lookup(
        segments_rows,
        fsw_column=segment_fsw_column,
        segment_id_column=segment_id_column,
    )

    missing_fsws = collect_missing_fsws(
        valid_inventories=valid_inventories,
        source_file_column=source_file_column,
        source_folder_column=source_folder_column,
        family_configs=family_configs,
        segments_lookup=segments_lookup,
    )

    if missing_fsws:
        print("\nThe following FSW values were found in inventory source files but not in segments.csv:")
        for fsw in missing_fsws:
            print(f"  - {fsw}")
        print("\nPlease update segments.csv with these FSW values before generating inventory pages.")
        print("Cancelled.")
        return

    generated = 0

    for inv in valid_inventories:
        source_code = inv[source_file_column].strip()
        family = get_source_family(source_code)

        if family not in family_configs:
            print(f"Skipping {inv[inventory_id_column]}: no configuration found for source family {family}.")
            continue

        source_file = find_matching_file(
            inv[source_folder_column],
            inv[source_file_column],
        )

        if not source_file:
            print(f"Skipping {inv[inventory_id_column]}: no matching source file found.")
            continue

        source_rows = load_csv(source_file)

        config = family_configs[family]
        source_fsw_column = config["source_fsw_column"]

        source_rows = [
            row for row in source_rows
            if row.get(source_fsw_column, "").strip() != ""
        ]

        joined_rows = join_inventory_rows(
            source_rows,
            source_fsw_column=source_fsw_column,
            segments_lookup=segments_lookup,
            segment_columns_to_add=segment_columns_to_add,
        )

        final_columns_to_show = list(segment_columns_to_add)

        title = inv[inventory_title_column]
        metadata_html = render_inventory_metadata(inv)
        table_html = render_table(
            rows=joined_rows,
            columns_to_show=final_columns_to_show,
            fsw_column=segment_fsw_column,
        )

        output_path = Path(output_folder) / f"{inv[inventory_id_column]}.html"
        write_inventory_page(output_path, title, metadata_html, table_html)
        generated += 1

    print(f"\nCreated {generated} inventory page(s) in: {output_folder}")


if __name__ == "__main__":
    main()
