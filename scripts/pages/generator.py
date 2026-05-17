import csv
import html
from pathlib import Path

PAGE_CSS = """
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

body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  margin: 0;
  background-color: #f8f9fb;
  color: #222;
}

.page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.site-nav {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.site-nav a {
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background-color: white;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.page-description {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #555;
  line-height: 1.5;
}

.table-search {
  width: 100%;
  max-width: 420px;
  box-sizing: border-box;
  margin-bottom: 1rem;
  padding: 0.7rem 0.9rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font: inherit;
  background-color: white;
}

.table-search:focus {
  outline: 2px solid #c7d2fe;
  border-color: #6b7280;
}

.table-container {
  max-height: 70vh;
  overflow: auto;
  border-radius: 12px;
  background-color: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

table {
  width: 100%;
  min-width: 100%;
  border-collapse: collapse;
  background-color: white;
}

thead {
  background-color: #eef1f5;
}

thead th {
  position: sticky;
  top: 0;
  z-index: 2;
  background-color: #eef1f5;
}

th,
td {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid #ddd;
  text-align: left;
}

th {
  vertical-align: top;
  font-size: 0.9rem;
  font-weight: 700;
  color: #333;
}

th span {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #555;
}

td {
  vertical-align: middle;
  font-size: 0.95rem;
}

.col-language-name {
  white-space: normal;
  min-width: 260px;
  max-width: 520px;
  overflow-wrap: break-word;
}

.col-inventory-name {
  white-space: normal;
  min-width: 220px;
  max-width: 340px;
  overflow-wrap: break-word;
}

.col-contributor,
.col-cite {
  white-space: normal;
  max-width: 260px;
  overflow-wrap: break-word;
}

.col-glottocode,
.col-iso-639-3 {
  white-space: normal;
  min-width: 120px;
}

.col-language-abbreviation,
.col-macro-area,
.col-ct-handshapes,
.col-fsw,
.col-signwriting-1,
.col-signwriting-2 {
  white-space: nowrap;
}

tbody tr:hover {
  background-color: #f4f7fb;
}

a {
  color: #5b2ea6;
  font-weight: 700;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.signwriting {
  font-family: "SuttonSignWritingOneD", "SuttonSignWritingLine", "SuttonSignWritingFill";
  font-size: 1.8em;
  text-align: center;
  white-space: nowrap;
}

.empty-cell {
  color: #aaa;
}

@media (max-width: 700px) {
  .page {
    max-width: 100%;
    padding: 0.75rem;
  }

  .site-nav {
    gap: 0.35rem;
    margin-bottom: 1.25rem;
  }

  .site-nav a {
    font-size: 0.86rem;
    padding: 0.39rem 0.64rem;
  }

  h1,
  h2 {
    font-size: 1.25rem;
    line-height: 1.2;
  }

  .language-title {
    max-width: 100%;
  }

  .title-extra {
    font-size: 0.72em;
  }

  .page-description {
    font-size: 0.95rem;
    line-height: 1.4;
  }

  .content-card {
    margin-top: 1rem;
    padding: 1rem;
    border-radius: 10px;
  }

  .table-search {
    max-width: 100%;
    font-size: 0.95rem;
    padding: 0.6rem 0.75rem;
  }

  .table-container,
  .metadata-table-container {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  table {
    min-width: 560px;
  }

  th,
  td {
    padding: 0.6rem 0.75rem;
    font-size: 0.9rem;
  }

  .signwriting {
    font-size: 1.5em;
  }
}
</style>
"""

TABLE_FILTER_SCRIPT = """
<script>
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("table-search");
  const tableRows = document.querySelectorAll("tbody tr");

  if (!searchInput) {
    return;
  }

  searchInput.addEventListener("input", function () {
    const query = searchInput.value.toLowerCase();

    tableRows.forEach(function (row) {
      const rowText = row.textContent.toLowerCase();

      if (rowText.includes(query)) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  });
});
</script>
"""


def choose_csv_path():
    default_csv_paths = {
        "1": ("Inventories", "data/slphoible/inventories.csv"),
        "2": ("Segments", "data/slphoible/segments.csv"),
        "3": ("Languages", "data/slphoible/languages.csv"),
    }

    print("\nChoose a CSV file:")

    for number, (label, path) in default_csv_paths.items():
        print(f"{number}. {label} — {path}")

    while True:
        choice = input("> ").strip()

        if choice in default_csv_paths:
            return default_csv_paths[choice][1]

        print("Please enter 1, 2, or 3.")


def load_csv(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def show_columns(columns):
    print("\nAvailable columns:")

    for i, col in enumerate(columns, start=1):
        print(f"{i}. {col}")


def prompt_with_default(label, default_value):
    value = input(
        f"\n{label} [{default_value}] (Enter = default): "
    ).strip()

    if value == "":
        return default_value

    return value


def format_columns_with_numbers(columns, selected_columns):
    formatted_columns = []

    for selected_column in selected_columns:
        column_number = columns.index(selected_column) + 1
        formatted_columns.append(f"{column_number}. {selected_column}")

    return ", ".join(formatted_columns)


def format_column_with_number(columns, selected_column):
    column_number = columns.index(selected_column) + 1
    return f"{column_number}. {selected_column}"


def prompt_columns_with_default(columns, label, default_columns):
    default_text = format_columns_with_numbers(columns, default_columns)

    raw = input(
        f"\n{label} [{default_text}] (Enter = default, or type numbers): "
    ).strip()

    if raw == "":
        return default_columns

    indices = [int(x.strip()) - 1 for x in raw.split(",")]
    return [columns[i] for i in indices]


def prompt_column_with_default(columns, label, default_column):
    default_text = format_column_with_number(columns, default_column)

    raw = input(
        f"\n{label} [{default_text}] (Enter = default, or type number): "
    ).strip()

    if raw == "":
        return default_column

    return columns[int(raw) - 1]


def build_link(cell_value, row_id, target_folder):
    href = f"{target_folder}/{row_id}.html"
    return f'<a href="{html.escape(href)}">{html.escape(cell_value)}</a>'


def format_header(column_name):
    special_headers = {
        "fsw": "FSW",
        "ISO-639-3": "ISO 639-3",
        "ct_handshapes": "Handshape<br><span>Count</span>",
        "hamnosys_1_initial_configuration": "HamNoSys&nbsp;1<br><span>Initial Configuration</span>",
        "hamnosys_2_basic_handshape": "HamNoSys&nbsp;2<br><span>Basic Handshape</span>",
        "hamnosys_3_handshape_modifications": "HamNoSys&nbsp;3<br><span>Handshape Modifications</span>",
    }

    if column_name in special_headers:
        return special_headers[column_name]

    return html.escape(column_name.replace("_", " ").title())


def format_cell_value(column_name, value):
    if column_name in ["glottocode", "ISO-639-3"] and "," in value:
        values = [html.escape(part.strip()) for part in value.split(",")]
        return "<br>".join(values)

    return html.escape(value)


def render_search_box():
    return (
        '<input id="table-search" class="table-search" type="search" '
        'placeholder="Type to filter rows...">'
    )


def render_site_nav():
    return """
<nav class="site-nav">
  <a href="index.html">Home</a>
  <a href="segments.html">Segments</a>
  <a href="inventories.html">Inventories</a>
  <a href="languages.html">Languages</a>
</nav>
"""


def render_table(rows, columns_to_show, id_column=None, clickable_column=None, target_folder=None):
    parts = []
    parts.append(render_search_box())
    parts.append('<div class="table-container">')
    parts.append("<table>")
    parts.append("<thead><tr>")

    for col in columns_to_show:
        column_class = f"col-{col.replace('_', '-').lower()}"
        parts.append(f'<th class="{column_class}">{format_header(col)}</th>')

    parts.append("</tr></thead>")
    parts.append("<tbody>")

    for row in rows:
        parts.append("<tr>")

        for col in columns_to_show:
            value = row.get(col, "").strip()
            column_class = f"col-{col.replace('_', '-').lower()}"

            if (
                clickable_column == col
                and target_folder
                and id_column
                and row.get(id_column, "")
                and value
            ):
                cell = build_link(value, row[id_column], target_folder)
            elif value == "":
                cell = '<span class="empty-cell">—</span>'
            else:
                cell = format_cell_value(col, value)

            if col.startswith("signwriting"):
                parts.append(f'<td class="signwriting {column_class}">{cell}</td>')
            else:
                parts.append(f'<td class="{column_class}">{cell}</td>')

        parts.append("</tr>")

    parts.append("</tbody></table>")
    parts.append("</div>")

    return "\n".join(parts)


def write_page(output_path, title, table_html, description=None):
    description_html = ""

    if description:
        description_html = f'<p class="page-description">{html.escape(description)}</p>'

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  {PAGE_CSS}
</head>
<body>
  <main class="page">
    {render_site_nav()}
    <h1>{html.escape(title)}</h1>
    {description_html}
    {table_html}
  </main>
  {TABLE_FILTER_SCRIPT}
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
            "output_path": "docs/inventories.html",
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
            "description": "This page lists handshape inventories currently included in the repository. A single sign language may have more than one inventory when data comes from different sources or datasets. See the Home page for more information about the dataset sources.",
        }

    if file_name.startswith("segments") and Path(csv_path).suffix == ".csv":
        return {
            "output_path": "docs/segments.html",
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
            "description": "This page lists the segment symbols used in the repository. At this stage, the data centers on handshapes, with values represented through HamNoSys and Formal SignWriting.",
        }

    if file_name.startswith("languages") and Path(csv_path).suffix == ".csv":
        return {
            "output_path": "docs/languages.html",
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
"description": "This page lists the sign languages represented in the repository. Abbreviations generally follow common usage. Where multiple abbreviations exist, all are included. Shared abbreviations are distinguished with country labels. For combined language entries, a custom abbreviation was created. Languages without a Glottocode or ISO 639-3 code are marked as (none). See the Home page for more information about how languages were identified.",
        }

    return None


def get_settings_from_defaults(columns, defaults):
    print("\n--- CSV columns ---")
    show_columns(columns)

    output_path = prompt_with_default(
        "Output HTML filename or path",
        defaults["output_path"],
    )

    title = prompt_with_default(
        "Page title",
        defaults["title"],
    )

    columns_to_show = prompt_columns_with_default(
        columns,
        "Columns to display in the HTML table",
        defaults["columns_to_show"],
    )

    filter_column = prompt_column_with_default(
        columns,
        "Column used to keep only valid rows",
        defaults["filter_column"],
    )

    id_prefix = prompt_with_default(
        "Prefix that indicates a valid row",
        defaults["id_prefix"],
    )

    clickable_column = prompt_column_with_default(
        columns,
        "Column whose values should become clickable links",
        defaults["clickable_column"],
    )

    id_column = prompt_column_with_default(
        columns,
        "ID column used to build page links",
        defaults["id_column"],
    )

    target_folder = prompt_with_default(
        "Target folder for page links",
        defaults["target_folder"],
    )

    return {
        "output_path": output_path,
        "title": title,
        "columns_to_show": columns_to_show,
        "filter_column": filter_column,
        "id_prefix": id_prefix,
        "clickable_column": clickable_column,
        "id_column": id_column,
        "target_folder": target_folder,
        "description": defaults.get("description"),
    }


def main():
    print()
    print("This program converts a known SL-PHOIBLE CSV file into an HTML table page.")
    print("For inventories.csv, segments.csv, and languages.csv, it suggests default settings automatically.")

    csv_path = choose_csv_path()

    rows = load_csv(csv_path)

    if not rows:
        print("CSV is empty.")
        return

    columns = list(rows[0].keys())
    defaults = get_known_defaults(csv_path)

    if not defaults:
        print(f"No defaults found for: {csv_path}")
        print("Add this CSV to get_known_defaults() before generating a page.")
        return

    print("\nDetected known CSV file.")
    print("Press Enter to keep each default, or type a replacement value.")

    settings = get_settings_from_defaults(columns, defaults)

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

    write_page(
        settings["output_path"],
        settings["title"],
        table_html,
        description=settings.get("description"),
    )

    print(f"\nCreated: {settings['output_path']}")


if __name__ == "__main__":
    main()
