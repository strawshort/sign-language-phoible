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


def choose_columns(columns):
    raw = input("\nEnter column numbers to display, separated by commas: ").strip()
    indices = [int(x.strip()) - 1 for x in raw.split(",")]
    return [columns[i] for i in indices]


def choose_one_column(columns, prompt):
    raw = input(f"\n{prompt} (enter column number, or leave blank): ").strip()
    if raw == "":
        return None
    return columns[int(raw) - 1]


def build_link(cell_value, row_id, target_folder):
    href = f"{target_folder}/{row_id}.html"
    return f'<a href="{html.escape(href)}">{html.escape(cell_value)}</a>'


def render_table(rows, columns_to_show, id_column=None, clickable_column=None, target_folder=None):
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


def write_page(output_path, title, table_html):
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
  {table_html}
</body>
</html>
"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def main():
    csv_path = input("Input CSV path: ").strip()
    output_path = input("Output HTML path: ").strip()
    title = input("Page title: ").strip()

    rows = load_csv(csv_path)
    if not rows:
        print("CSV is empty.")
        return

    columns = list(rows[0].keys())
    show_columns(columns)

    columns_to_show = choose_columns(columns)
    id_column = choose_one_column(columns, "Select the ID column")
    clickable_column = choose_one_column(columns, "Select the clickable column")

    target_folder = None
    if clickable_column:
        target_folder = input(
            "Target folder for links (example: segments or inventories): "
        ).strip()

    table_html = render_table(
        rows=rows,
        columns_to_show=columns_to_show,
        id_column=id_column,
        clickable_column=clickable_column,
        target_folder=target_folder,
    )

    write_page(output_path, title, table_html)
    print(f"\nCreated: {output_path}")


if __name__ == "__main__":
    main()
