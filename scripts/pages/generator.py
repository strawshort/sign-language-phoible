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
    raw = input("> ").strip()
    indices = [int(x.strip()) - 1 for x in raw.split(",")]
    return [columns[i] for i in indices]


def choose_one_column(columns, prompt):
    print(f"\n{prompt}")
    raw = input("> ").strip()
    return columns[int(raw) - 1]


def build_link(cell_value, row_id, target_folder):
    href = f"{target_folder}/{row_id}.html"
    return f'<a href="{html.escape(href)}">{html.escape(cell_value)}</a>'


def format_header(column_name):
    return column_name.replace("_", " ").title()


def render_table(rows, columns_to_show, id_column=None, clickable_column=None, target_folder=None):
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
            if (
                clickable_column == col
                and target_folder
                and id_column
                and row.get(id_column, "")
            ):
                cell = build_link(value, row[id_column], target_folder)
            else:
                cell = html.escape(value)
            parts.append(f"<td>{cell}</td>")
        parts.append("</tr>")

    parts.append("</tbody></table>")
    return "\n".join(parts)


def write_page(output_path, title, table_html):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  {table_html}
</body>
</html>
"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def get_known_defaults(csv_path):
    file_name = Path(csv_path).name

    if file_name.startswith("inventories") and Path(csv_path).suffix == ".csv":
        return {
            "output_path": "inventories.html",
            "title": "Inventories",
            "columns_to_show": [
                "inventory_name",
                "language_name",
                "ct_handshapes",
                "contributor",
                "cite",
            ],
            "id_column": "inventory_id",
            "clickable_column": "inventory_name",
            "filter_column": "inventory_id",
            "id_prefix": "inv",
            "target_folder": "inventories",
        }

    if file_name.startswith("segments") and Path(csv_path).suffix == ".csv":
        return {
            "output_path": "segments.html",
            "title": "Segments",
            "columns_to_show": [
                "segment_class",
                "hamnosys_1_initial_configuration",
                "hamnosys_2_basic_handshape",
                "hamnosys_3_handshape_modifications",
                "fsw",
                "signwriting_1",
                "signwriting_2",
            ],
            "id_column": "segment_id",
            "clickable_column": "fsw",
            "filter_column": "segment_id",
            "id_prefix": "seg",
            "target_folder": "segments",
        }

    if file_name.startswith("languages") and Path(csv_path).suffix == ".csv":
        return {
            "output_path": "languages.html",
            "title": "Languages",
            "columns_to_show": [
                "language_name",
                "language_abbreviation",
                "glottocode",
                "ISO-639-3",
                "macro-area",
            ],
            "id_column": "language_id",
            "clickable_column": "language_name",
            "filter_column": "language_id",
            "id_prefix": "lan",
            "target_folder": "languages",
        }

    return None


def get_manual_settings(columns):
    print("\n--- CSV columns ---")
    show_columns(columns)

    output_path = input(
        "\nEnter the output HTML filename or path: "
    ).strip()

    title = input(
        "Enter the page title to display at the top of the HTML page: "
    ).strip()

    columns_to_show = choose_columns(
        columns,
        "Enter the column numbers to display in the HTML table, separated by commas.\n"
        "Suggested column selections: choose the columns you want shown on the page.",
    )

    filter_column = choose_one_column(
        columns,
        "Select the column used to keep only valid rows (for example, an ID column):",
    )

    id_prefix = input(
        "\nEnter the prefix in that column that indicates a valid row: "
    ).strip()

    add_links = input(
        "\nDo you want to add clickable links to one of the displayed columns? (y/n): "
    ).strip().lower()

    clickable_column = None
    id_column = None
    target_folder = None

    if add_links == "y":
        clickable_column = choose_one_column(
            columns,
            "Select the column whose values should become clickable links:",
        )

        id_column = choose_one_column(
            columns,
            "Select the ID column used to build those page links:",
        )

        target_folder = input(
            "\nEnter the target folder for those links: "
        ).strip()

    return {
        "output_path": output_path,
        "title": title,
        "columns_to_show": columns_to_show,
        "filter_column": filter_column,
        "id_prefix": id_prefix,
        "clickable_column": clickable_column,
        "id_column": id_column,
        "target_folder": target_folder,
    }


def main():
    print()
    print("This program converts a CSV file into an HTML table page with optional clickable links.")
    print("For inventories.csv, segments.csv, and languages.csv, it suggests default settings automatically.")

    csv_path = input(
        "\nEnter the CSV path for the file that you want to convert to HTML: "
        "(for example: data/slphoible/segments.csv, data/slphoible/inventories.csv, or data/slphoible/languages.csv): "
    ).strip()

    rows = load_csv(csv_path)
    if not rows:
        print("CSV is empty.")
        return

    columns = list(rows[0].keys())
    defaults = get_known_defaults(csv_path)

    if defaults:
        print("\nDetected known CSV file.")
        print(f"Suggested output HTML path: {defaults['output_path']}")
        print(f"Suggested page title: {defaults['title']}")
        print("Suggested columns to display: " + ", ".join(defaults["columns_to_show"]))
        print(f"Suggested ID column: {defaults['id_column']}")
        print(f"Suggested clickable column: {defaults['clickable_column']}")
        print(f"Suggested filter column: {defaults['filter_column']}")
        print(f"Suggested valid ID prefix: {defaults['id_prefix']}")
        print(f"Suggested target folder: {defaults['target_folder']}")

        use_defaults = input("\nUse these defaults? (y/n): ").strip().lower()

        if use_defaults == "y":
            settings = defaults
        else:
            settings = get_manual_settings(columns)
    else:
        settings = get_manual_settings(columns)

    rows = [
        row for row in rows
        if row.get(settings["filter_column"], "").strip().startswith(settings["id_prefix"])
    ]

    table_html = render_table(
        rows=rows,
        columns_to_show=settings["columns_to_show"],
        id_column=settings["id_column"],
        clickable_column=settings["clickable_column"],
        target_folder=settings["target_folder"],
    )

    write_page(settings["output_path"], settings["title"], table_html)
    print(f"\nCreated: {settings['output_path']}")


if __name__ == "__main__":
    main()
