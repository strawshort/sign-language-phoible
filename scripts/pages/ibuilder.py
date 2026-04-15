import csv
import html
from pathlib import Path


def load_csv(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def show_columns(columns):
    print("\nAvailable columns:")
    for i, col in enumerate(columns, start=1):
        print(f"{i}. {col}")


def choose_columns(columns, prompt):
    print(f"\n{prompt}")
    show_columns(columns)
    raw = input("\nEnter column numbers, separated by commas: ").strip()
    indices = [int(x.strip()) - 1 for x in raw.split(",")]
    return [columns[i] for i in indices]


def choose_one_column(columns, prompt):
    print(f"\n{prompt}")
    show_columns(columns)
    raw = input("\nEnter one column number: ").strip()
    return columns[int(raw) - 1]


def find_matching_file(folder, source_code):
    folder_path = Path(folder)
    matches = list(folder_path.glob(f"{source_code}_*.csv"))
    if not matches:
        return None
    return matches[0]


def build_segments_lookup(segments_rows, fsw_column, segment_id_column, segment_class_column):
    lookup = {}
    for row in segments_rows:
        fsw = row.get(fsw_column, "").strip()
        if fsw:
            lookup[fsw] = {
                "segment_id": row.get(segment_id_column, "").strip(),
                "segment_class": row.get(segment_class_column, "").strip(),
            }
    return lookup


def join_inventory_rows(source_rows, source_fsw_column, segments_lookup):
    joined = []
    for row in source_rows:
        fsw_value = row.get(source_fsw_column, "").strip()
        segment_info = segments_lookup.get(fsw_value, {"segment_id": "", "segment_class": ""})

        new_row = dict(row)
        new_row["segment_id"] = segment_info["segment_id"]
        new_row["segment_class"] = segment_info["segment_class"]
        joined.append(new_row)

    return joined


def build_fsw_link(fsw_value, segment_id):
    if not segment_id:
        return html.escape(fsw_value)
    href = f"../segments/{segment_id}.html"
    return f'<a href="{html.escape(href)}">{html.escape(fsw_value)}</a>'


def render_table(rows, columns_to_show, fsw_column):
    parts = []
    parts.append("<table border='1' cellspacing='0' cellpadding='6'>")
    parts.append("<thead><tr>")

    for col in columns_to_show:
        parts.append(f"<th>{html.escape(col)}</th>")

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
            parts.append(f"<th>{html.escape(key)}</th>")
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
</head>
<body>
  <h1>{html.escape(title)}</h1>

  <h2>Inventory details</h2>
  {metadata_html}

  <h2>Segments</h2>
  {table_html}
</body>
</html>
"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def main():
    inventories_csv = input("Inventories CSV path: ").strip()
    segments_csv = input("Segments CSV path: ").strip()
    output_folder = input("Output folder for inventory pages (example: inventories): ").strip()
    page_count = int(input("How many inventory pages to generate? ").strip())

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

    segment_id_column = choose_one_column(segments_columns, "Select the segment ID column from segments.csv")
    segment_fsw_column = choose_one_column(segments_columns, "Select the FSW column from segments.csv")
    segment_class_column = choose_one_column(segments_columns, "Select the segment class column from segments.csv")

    source_file_column = choose_one_column(inventories_columns, "Select the source code column from inventories.csv")
    source_folder_column = choose_one_column(inventories_columns, "Select the source folder column from inventories.csv")
    inventory_id_column = choose_one_column(inventories_columns, "Select the inventory ID column from inventories.csv")
    inventory_title_column = choose_one_column(inventories_columns, "Select the inventory title column from inventories.csv")

    first_inventory_file = None
    for inv in inventories_rows[:page_count]:
        first_inventory_file = find_matching_file(
            inv[source_folder_column],
            inv[source_file_column],
        )
        if first_inventory_file:
            break

    if not first_inventory_file:
        print("No matching inventory source file found.")
        return

    sample_source_rows = load_csv(first_inventory_file)
    if not sample_source_rows:
        print("The sample inventory source CSV is empty.")
        return

    source_columns = list(sample_source_rows[0].keys())
    source_fsw_column = choose_one_column(source_columns, "Select the FSW column from the inventory source files")
    source_display_columns = choose_columns(
        source_columns,
        "Select the columns from the inventory source files to display on the inventory pages",
    )

    add_segment_class = input("\nAdd segment_class to the displayed table? (y/n): ").strip().lower() == "y"
    if add_segment_class and "segment_class" not in source_display_columns:
        source_display_columns = ["segment_class"] + source_display_columns

    segments_lookup = build_segments_lookup(
        segments_rows,
        fsw_column=segment_fsw_column,
        segment_id_column=segment_id_column,
        segment_class_column=segment_class_column,
    )

    generated = 0

    for inv in inventories_rows[:page_count]:
        source_file = find_matching_file(
            inv[source_folder_column],
            inv[source_file_column],
        )

        if not source_file:
            print(f"Skipping {inv[inventory_id_column]}: no matching source file found.")
            continue

        source_rows = load_csv(source_file)
        joined_rows = join_inventory_rows(
            source_rows,
            source_fsw_column=source_fsw_column,
            segments_lookup=segments_lookup,
        )

        title = inv[inventory_title_column]
        metadata_html = render_inventory_metadata(inv)
        table_html = render_table(
            rows=joined_rows,
            columns_to_show=source_display_columns,
            fsw_column=source_fsw_column,
        )

        output_path = Path(output_folder) / f"{inv[inventory_id_column]}.html"
        write_inventory_page(output_path, title, metadata_html, table_html)
        generated += 1

    print(f"\nCreated {generated} inventory page(s) in: {output_folder}")


if __name__ == "__main__":
    main()
