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


def find_matching_file(folder, source_code):
    folder_path = Path(folder)
    matches = sorted(folder_path.glob(f"{source_code}_*.csv"))
    if not matches:
        return None
    return matches[0]


def get_source_family(source_code):
    return source_code.split("_")[0].strip()


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


def render_segment_details(segment_row, columns_to_show):
    parts = []
    parts.append("<table border='1' cellspacing='0' cellpadding='6'>")
    parts.append("<tbody>")

    for col in columns_to_show:
        parts.append("<tr>")
        parts.append(f"<th>{html_escape(format_header(col))}</th>")
        parts.append(f"<td>{html_escape(segment_row.get(col, ''))}</td>")
        parts.append("</tr>")

    parts.append("</tbody></table>")
    return "\n".join(parts)


def render_inventory_table(
    matching_inventories,
    inventory_id_column,
    inventory_name_column,
    language_name_column,
    source_label_column,
):
    if not matching_inventories:
        return "<p>No inventories found for this segment.</p>"

    parts = []
    parts.append("<table border='1' cellspacing='0' cellpadding='6'>")
    parts.append("<thead><tr>")
    parts.append("<th>Inventory</th>")
    parts.append("<th>Language</th>")
    parts.append("<th>Source</th>")
    parts.append("</tr></thead>")
    parts.append("<tbody>")

    for row in matching_inventories:
        inv_id = row.get(inventory_id_column, "")
        inv_name = row.get(inventory_name_column, "")
        language = row.get(language_name_column, "")
        source = row.get(source_label_column, "")

        link = f"../inventories/{inv_id}.html"

        parts.append("<tr>")
        parts.append(f'<td><a href="{html_escape(link)}">{html_escape(inv_name)}</a></td>')
        parts.append(f"<td>{html_escape(language)}</td>")
        parts.append(f"<td>{html_escape(source)}</td>")
        parts.append("</tr>")

    parts.append("</tbody></table>")
    return "\n".join(parts)


def write_segment_page(output_path, title, details_html, inventory_table_html):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_escape(title)}</title>
</head>
<body>
  <h1>{html_escape(title)}</h1>

  <h2>Segment Details</h2>
  {details_html}

  <h2>Inventories Containing This Segment</h2>
  {inventory_table_html}
</body>
</html>
"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def get_known_defaults(segments_csv, inventories_csv):
    seg_norm = str(Path(segments_csv)).replace("\\", "/").lower()
    inv_norm = str(Path(inventories_csv)).replace("\\", "/").lower()

    if seg_norm.endswith("segments.csv") and inv_norm.endswith("inventories.csv"):
        return {
            "output_folder": "segments",
            "segment_id_column": "segment_id",
            "segment_fsw_column": "fsw",
            "segment_class_column": "segment_class",
            "segment_detail_columns": [
                "segment_id",
                "segment_class",
                "hamnosys_1_initial_configuration",
                "hamnosys_2_basic_handshape",
                "hamnosys_3_handshape_modifications",
                "fsw",
                "signwriting_1",
                "signwriting_2",
            ],
            "inventory_id_column": "inventory_id",
            "inventory_name_column": "inventory_name",
            "language_name_column": "language_name",
            "contributor_column": "contributor",
            "year_column": "year",
            "data_source_column": "data_source",
            "data_source_location_column": "data_source_location",
        }

    return None


def main():
    print()
    print("This program creates individual segment HTML pages from segments.csv.")
    print("Each segment page shows the segment details and the inventories that contain that segment.")

    segments_csv = input(
        "\nEnter the path to the segments CSV "
        "(for example: data/slphoible/segments.csv): "
    ).strip()

    inventories_csv = input(
        "Enter the path to the inventories CSV "
        "(for example: data/slphoible/inventories.csv): "
    ).strip()

    segments_rows = load_csv(segments_csv)
    inventories_rows = load_csv(inventories_csv)

    if not segments_rows:
        print("Segments CSV is empty.")
        return
    if not inventories_rows:
        print("Inventories CSV is empty.")
        return

    segment_columns = list(segments_rows[0].keys())
    inventory_columns = list(inventories_rows[0].keys())

    defaults = get_known_defaults(segments_csv, inventories_csv)

    if defaults:
        print("\nDetected known CSV files.")
        print(f"\nSuggested output folder: {defaults['output_folder']}")

        print("\nSuggested default columns from segments.csv:")
        print(f"  ID column: {defaults['segment_id_column']}")
        print(f"  FSW column: {defaults['segment_fsw_column']}")
        print(f"  Segment class column: {defaults['segment_class_column']}")
        print("  Segment detail columns: " + ", ".join(defaults["segment_detail_columns"]))

        print("\nSuggested default columns from inventories.csv:")
        print(f"  Inventory ID column: {defaults['inventory_id_column']}")
        print(f"  Inventory name column: {defaults['inventory_name_column']}")
        print(f"  Language name column: {defaults['language_name_column']}")
        print(f"  Contributor column: {defaults['contributor_column']}")
        print(f"  Year column: {defaults['year_column']}")
        print(f"  Data source column: {defaults['data_source_column']}")
        print(f"  Data source location column: {defaults['data_source_location_column']}")

        use_defaults = input("\nUse these defaults? (y/n): ").strip().lower()

        if use_defaults == "y":
            output_folder = defaults["output_folder"]
            segment_id_column = defaults["segment_id_column"]
            segment_fsw_column = defaults["segment_fsw_column"]
            segment_class_column = defaults["segment_class_column"]
            segment_detail_columns = defaults["segment_detail_columns"]
            inventory_id_column = defaults["inventory_id_column"]
            inventory_name_column = defaults["inventory_name_column"]
            language_name_column = defaults["language_name_column"]
            contributor_column = defaults["contributor_column"]
            year_column = defaults["year_column"]
            data_source_column = defaults["data_source_column"]
            data_source_location_column = defaults["data_source_location_column"]
        else:
            output_folder = input(
                "\nEnter the output folder for the segment pages "
                "(for example: segments): "
            ).strip()

            print("\n--- segments.csv columns ---")
            show_columns(segment_columns)
            segment_id_column = choose_one_column(segment_columns, "Select the segment ID column from segments.csv")
            segment_fsw_column = choose_one_column(segment_columns, "Select the FSW column from segments.csv")
            segment_class_column = choose_one_column(segment_columns, "Select the segment class column from segments.csv")
            segment_detail_columns = choose_columns(
                segment_columns,
                "Enter the column numbers to show in the segment details table, separated by commas:"
            )

            print("\n--- inventories.csv columns ---")
            show_columns(inventory_columns)
            inventory_id_column = choose_one_column(inventory_columns, "Select the inventory ID column from inventories.csv")
            inventory_name_column = choose_one_column(inventory_columns, "Select the inventory name column from inventories.csv")
            language_name_column = choose_one_column(inventory_columns, "Select the language name column from inventories.csv")
            contributor_column = choose_one_column(inventory_columns, "Select the contributor column from inventories.csv")
            year_column = choose_one_column(inventory_columns, "Select the year column from inventories.csv")
            data_source_column = choose_one_column(inventory_columns, "Select the data source column from inventories.csv")
            data_source_location_column = choose_one_column(inventory_columns, "Select the data source location column from inventories.csv")
    else:
        output_folder = input(
            "\nEnter the output folder for the segment pages "
            "(for example: segments): "
        ).strip()

        print("\n--- segments.csv columns ---")
        show_columns(segment_columns)
        segment_id_column = choose_one_column(segment_columns, "Select the segment ID column from segments.csv")
        segment_fsw_column = choose_one_column(segment_columns, "Select the FSW column from segments.csv")
        segment_class_column = choose_one_column(segment_columns, "Select the segment class column from segments.csv")
        segment_detail_columns = choose_columns(
            segment_columns,
            "Enter the column numbers to show in the segment details table, separated by commas:"
        )

        print("\n--- inventories.csv columns ---")
        show_columns(inventory_columns)
        inventory_id_column = choose_one_column(inventory_columns, "Select the inventory ID column from inventories.csv")
        inventory_name_column = choose_one_column(inventory_columns, "Select the inventory name column from inventories.csv")
        language_name_column = choose_one_column(inventory_columns, "Select the language name column from inventories.csv")
        contributor_column = choose_one_column(inventory_columns, "Select the contributor column from inventories.csv")
        year_column = choose_one_column(inventory_columns, "Select the year column from inventories.csv")
        data_source_column = choose_one_column(inventory_columns, "Select the data source column from inventories.csv")
        data_source_location_column = choose_one_column(inventory_columns, "Select the data source location column from inventories.csv")

    valid_segments = [
        row for row in segments_rows
        if row.get(segment_id_column, "").strip().startswith("seg")
    ]

    valid_inventories = [
        row for row in inventories_rows
        if row.get(inventory_id_column, "").strip().startswith("inv")
    ]

    if not valid_segments:
        print("No valid segment rows found.")
        return
    if not valid_inventories:
        print("No valid inventory rows found.")
        return

    print("\n--- Valid segments ---")
    for i, row in enumerate(valid_segments, start=1):
        print(
            f"{i}. {row.get(segment_id_column, '')} | "
            f"{row.get(segment_class_column, '')} | "
            f"{row.get(segment_fsw_column, '')}"
        )

    print("\nChoose segments to build:")
    print("  all = all valid segments")
    print("  0   = none")
    print("  1-5 = range")
    print("  1,4,7 = specific entries")
    selection = input("> ").strip().lower()

    chosen_indexes = parse_selection(selection, len(valid_segments))
    selected_segments = [valid_segments[i] for i in chosen_indexes]

    if not selected_segments:
        print("No segments selected.")
        return

    inventories_by_family = {}
    for row in valid_inventories:
        source_code = row.get(data_source_column, "").strip()
        family = get_source_family(source_code)
        inventories_by_family.setdefault(family, []).append(row)

    family_fsw_columns = {}

    for family in sorted(inventories_by_family.keys()):
        family_rows = inventories_by_family[family]
        sample_row = family_rows[0]
        sample_file = find_matching_file(
            sample_row.get(data_source_location_column, "").strip(),
            sample_row.get(data_source_column, "").strip(),
        )

        if not sample_file:
            print(f"\nSkipping source family {family}: no matching sample file found.")
            continue

        sample_rows = load_csv(sample_file)
        if not sample_rows:
            print(f"\nSkipping source family {family}: sample file is empty.")
            continue

        source_columns = list(sample_rows[0].keys())

        print(f"\n--- Columns for source family: {family} ---")
        show_columns(source_columns)
        family_fsw_columns[family] = choose_one_column(
            source_columns,
            f"Select the FSW column for all {family} source files"
        )

    inventory_fsw_lookup = {}

    print("\nScanning inventory files...")
    for inv in valid_inventories:
        source_code = inv.get(data_source_column, "").strip()
        source_folder = inv.get(data_source_location_column, "").strip()
        family = get_source_family(source_code)

        source_file = find_matching_file(source_folder, source_code)
        if not source_file:
            continue

        if family not in family_fsw_columns:
            continue

        source_rows = load_csv(source_file)
        fsw_column = family_fsw_columns[family]

        fsw_values = {
            row.get(fsw_column, "").strip()
            for row in source_rows
            if row.get(fsw_column, "").strip() != ""
        }

        inventory_fsw_lookup[inv.get(inventory_id_column, "")] = fsw_values

    source_label_column = "_source_label_temp"

    for inv in valid_inventories:
        inv[source_label_column] = build_source_label(inv, contributor_column, year_column)

    generated = 0

    for segment_row in selected_segments:
        segment_id = segment_row.get(segment_id_column, "").strip()
        segment_fsw = segment_row.get(segment_fsw_column, "").strip()
        segment_class = segment_row.get(segment_class_column, "").strip()

        matching_inventories = []
        for inv in valid_inventories:
            inv_id = inv.get(inventory_id_column, "")
            inv_fsw_values = inventory_fsw_lookup.get(inv_id, set())
            if segment_fsw in inv_fsw_values:
                matching_inventories.append(inv)

        title = f"{segment_class.capitalize()} {segment_fsw}" if segment_class else segment_fsw
        details_html = render_segment_details(segment_row, segment_detail_columns)
        inventory_table_html = render_inventory_table(
            matching_inventories,
            inventory_id_column=inventory_id_column,
            inventory_name_column=inventory_name_column,
            language_name_column=language_name_column,
            source_label_column=source_label_column,
        )

        output_path = Path(output_folder) / f"{segment_id}.html"
        write_segment_page(output_path, title, details_html, inventory_table_html)
        generated += 1

    print(f"\nCreated {generated} segment page(s) in: {output_folder}")


if __name__ == "__main__":
    main()
