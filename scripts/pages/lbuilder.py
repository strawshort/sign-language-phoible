import csv
import html
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

PAGE_CSS = """
<style>
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

h1,
h2 {
  margin-top: 0;
  font-size: 1.5rem;
}

.language-title {
  line-height: 1.2;
  max-width: 1200px;
}

.title-extra {
  color: #888;
  font-size: 0.78em;
  font-weight: 500;
}

.page-description {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
  color: #555;
  line-height: 1.5;
}

.content-card .page-description {
  margin-bottom: 0;
}

.content-card {
  margin-top: 1.5rem;
  padding: 1.5rem;
  border-radius: 12px;
  background-color: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.content-card:first-of-type {
  margin-top: 0;
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

.metadata-table-container {
  overflow-x: auto;
  border-radius: 12px;
  background-color: white;
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

.metadata-table th {
  background-color: #eef1f5;
}

.col-language-id,
.col-language-abbreviation,
.col-glottocode,
.col-iso-639-3,
.col-macro-area,
.col-segments,
.col-handshapes {
  white-space: nowrap;
}

.col-inventory,
.col-source {
  white-space: normal;
  max-width: 420px;
  overflow-wrap: break-word;
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

.empty-cell {
  color: #aaa;
}
</style>
"""

TABLE_FILTER_SCRIPT = """
<script>
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("table-search");
  const tableRows = document.querySelectorAll(".filterable-table tbody tr");

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


def load_csv(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def show_columns(columns):
    print("\nAvailable columns:")

    for i, col in enumerate(columns, start=1):
        print(f"{i}. {col}")


def format_columns_with_numbers(columns, selected_columns):
    formatted_columns = []

    for selected_column in selected_columns:
        column_number = columns.index(selected_column) + 1
        formatted_columns.append(f"{column_number}. {selected_column}")

    return ", ".join(formatted_columns)


def format_column_with_number(columns, selected_column):
    column_number = columns.index(selected_column) + 1
    return f"{column_number}. {selected_column}"


def prompt_with_default(label, default_value):
    value = input(
        f"\n{label} [{default_value}] (Enter = default): "
    ).strip()

    if value == "":
        return default_value

    return value


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


def parse_selection(selection, max_index):
    selection = selection.strip().lower()

    if selection == "" or selection == "all":
        return list(range(max_index))

    if selection == "0":
        return []

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


def split_parenthetical_name(name):
    name = name.strip()

    if "(" not in name or not name.endswith(")"):
        return name, ""

    main_name, parenthetical = name.split("(", 1)
    return main_name.strip(), parenthetical.strip(")")


def render_language_title(title):
    main_name, components = split_parenthetical_name(title)

    if components:
        return (
            '<h1 class="language-title">'
            f'Language: {html.escape(main_name)} '
            f'<span class="title-extra">({html.escape(components)})</span>'
            '</h1>'
        )

    return (
        '<h1 class="language-title">'
        f'Language: {html.escape(main_name)}'
        '</h1>'
    )


def format_header(column_name):
    special_headers = {
        "ISO-639-3": "ISO 639-3",
    }

    if column_name in special_headers:
        return special_headers[column_name]

    return html.escape(column_name.replace("_", " ").title())


def format_cell_value(column_name, value):
    value = str(value).strip()

    if value == "":
        return '<span class="empty-cell">—</span>'

    if column_name in ["glottocode", "ISO-639-3"] and "," in value:
        values = [html.escape(part.strip()) for part in value.split(",")]
        return "<br>".join(values)

    return html.escape(value)


def column_class_name(column_name):
    return f"col-{column_name.replace('_', '-').lower()}"


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


def render_search_box():
    return (
        '<input id="table-search" class="table-search" type="search" '
        'placeholder="Type to filter rows...">'
    )


def render_site_nav():
    return """
<nav class="site-nav">
  <a href="../index.html">Home</a>
  <a href="../segments.html">Segments</a>
  <a href="../inventories.html">Inventories</a>
  <a href="../languages.html">Languages</a>
</nav>
"""


def render_language_details(language_row, columns_to_show):
    parts = []
    parts.append('<div class="metadata-table-container">')
    parts.append('<table class="metadata-table">')
    parts.append("<thead><tr>")

    for col in columns_to_show:
        column_class = column_class_name(col)
        parts.append(f'<th class="{column_class}">{format_header(col)}</th>')

    parts.append("</tr></thead>")
    parts.append("<tbody><tr>")

    for col in columns_to_show:
        value = language_row.get(col, "")
        column_class = column_class_name(col)
        parts.append(f'<td class="{column_class}">{format_cell_value(col, value)}</td>')

    parts.append("</tr></tbody>")
    parts.append("</table>")
    parts.append("</div>")

    return "\n".join(parts)


def render_inventory_table(
    matching_inventories,
    inventory_id_column,
    inventory_name_column,
    source_label_column,
    ct_segments_column,
    ct_handshapes_column,
):
    if not matching_inventories:
        return "<p>No inventories found for this language.</p>"

    parts = []
    parts.append(render_search_box())
    parts.append('<div class="table-container">')
    parts.append('<table class="filterable-table">')
    parts.append("<thead><tr>")
    parts.append('<th class="col-inventory">Inventory</th>')
    parts.append('<th class="col-source">Source</th>')
    parts.append('<th class="col-segments">Segments<br><span>Total</span></th>')
    parts.append('<th class="col-handshapes">Handshapes<br><span>Count</span></th>')
    parts.append("</tr></thead>")
    parts.append("<tbody>")

    for row in matching_inventories:
        inv_id = row.get(inventory_id_column, "").strip()
        inv_name = row.get(inventory_name_column, "").strip()
        source = row.get(source_label_column, "").strip()
        segments = row.get(ct_segments_column, "").strip()
        handshapes = row.get(ct_handshapes_column, "").strip()

        link = f"../inventories/{inv_id}.html"

        parts.append("<tr>")
        parts.append(f'<td class="col-inventory"><a href="{html.escape(link)}">{format_cell_value("inventory", inv_name)}</a></td>')
        parts.append(f'<td class="col-source">{format_cell_value("source", source)}</td>')
        parts.append(f'<td class="col-segments">{format_cell_value("segments", segments)}</td>')
        parts.append(f'<td class="col-handshapes">{format_cell_value("handshapes", handshapes)}</td>')
        parts.append("</tr>")

    parts.append("</tbody></table>")
    parts.append("</div>")

    return "\n".join(parts)


def write_language_page(output_path, title, details_html, inventory_section_html):
    description = "This page lists all the inventories associated with the specified sign language(s)."

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Language: {html.escape(title)}</title>
  {PAGE_CSS}
</head>
<body>
  <main class="page">
    {render_site_nav()}

    <section class="content-card">
      {render_language_title(title)}
      {details_html}
      <p class="page-description">{html.escape(description)}</p>
    </section>

    <section class="content-card">
      <h2>Inventories</h2>
      {inventory_section_html}
    </section>
  </main>
  {TABLE_FILTER_SCRIPT}
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
            "output_folder": "docs/languages",
            "language_id_column": "language_id",
            "language_name_column": "language_name",
            "language_detail_columns": [
                "language_id",
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
            "ct_handshapes_column": "ct_handshapes",
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


def get_settings_from_defaults(language_columns, inventory_columns, defaults):
    print("\nDetected known CSV files.")
    print("Press Enter to keep each default, or type a replacement value.")

    output_folder = prompt_with_default(
        "Output folder for language pages",
        defaults["output_folder"],
    )

    print("\n--- languages.csv columns ---")
    show_columns(language_columns)

    language_id_column = prompt_column_with_default(
        language_columns,
        "Language ID column from languages.csv",
        defaults["language_id_column"],
    )

    language_name_column = prompt_column_with_default(
        language_columns,
        "Language name column from languages.csv",
        defaults["language_name_column"],
    )

    language_detail_columns = prompt_columns_with_default(
        language_columns,
        "Columns to show in the language details table",
        defaults["language_detail_columns"],
    )

    print("\n--- inventories.csv columns ---")
    show_columns(inventory_columns)

    inventory_id_column = prompt_column_with_default(
        inventory_columns,
        "Inventory ID column from inventories.csv",
        defaults["inventory_id_column"],
    )

    inventory_name_column = prompt_column_with_default(
        inventory_columns,
        "Inventory name column from inventories.csv",
        defaults["inventory_name_column"],
    )

    inventory_language_name_column = prompt_column_with_default(
        inventory_columns,
        "Language name column from inventories.csv used for matching",
        defaults["inventory_language_name_column"],
    )

    contributor_column = prompt_column_with_default(
        inventory_columns,
        "Contributor column from inventories.csv",
        defaults["contributor_column"],
    )

    year_column = prompt_column_with_default(
        inventory_columns,
        "Year column from inventories.csv",
        defaults["year_column"],
    )

    ct_segments_column = prompt_column_with_default(
        inventory_columns,
        "Total segments column from inventories.csv",
        defaults["ct_segments_column"],
    )

    ct_handshapes_column = prompt_column_with_default(
        inventory_columns,
        "Handshape count column from inventories.csv",
        defaults["ct_handshapes_column"],
    )

    return {
        "output_folder": output_folder,
        "language_id_column": language_id_column,
        "language_name_column": language_name_column,
        "language_detail_columns": language_detail_columns,
        "inventory_id_column": inventory_id_column,
        "inventory_name_column": inventory_name_column,
        "inventory_language_name_column": inventory_language_name_column,
        "contributor_column": contributor_column,
        "year_column": year_column,
        "ct_segments_column": ct_segments_column,
        "ct_handshapes_column": ct_handshapes_column,
    }


def choose_known_csv_paths():
    languages_csv = prompt_with_default(
        "Languages CSV path",
        "data/slphoible/languages.csv",
    )

    inventories_csv = prompt_with_default(
        "Inventories CSV path",
        "data/slphoible/inventories.csv",
    )

    return languages_csv, inventories_csv


def main():
    print()
    print("This program creates individual language HTML pages from languages.csv.")
    print("Each language page shows the language details and the inventories that match that language.")

    languages_csv, inventories_csv = choose_known_csv_paths()

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

    if not defaults:
        print("\nNo defaults found for the selected CSV files.")
        print("Add these CSV files to get_known_defaults() before generating language pages.")
        return

    settings = get_settings_from_defaults(
        language_columns=language_columns,
        inventory_columns=inventory_columns,
        defaults=defaults,
    )

    output_folder = settings["output_folder"]
    language_id_column = settings["language_id_column"]
    language_name_column = settings["language_name_column"]
    language_detail_columns = settings["language_detail_columns"]
    inventory_id_column = settings["inventory_id_column"]
    inventory_name_column = settings["inventory_name_column"]
    inventory_language_name_column = settings["inventory_language_name_column"]
    contributor_column = settings["contributor_column"]
    year_column = settings["year_column"]
    ct_segments_column = settings["ct_segments_column"]
    ct_handshapes_column = settings["ct_handshapes_column"]

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

    source_label_column = "_source_label_temp"

    for inv in valid_inventories:
        inv[source_label_column] = build_source_label(inv, contributor_column, year_column)

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

    if languages_only or inventories_only:
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
                source_label_column=source_label_column,
                ct_segments_column=ct_segments_column,
                ct_handshapes_column=ct_handshapes_column,
            )
        else:
            inventory_section_html = f"<p>No inventories found for {html.escape(language_name)}.</p>"

        output_path = Path(output_folder) / f"{language_id}.html"
        write_language_page(output_path, language_name, details_html, inventory_section_html)
        generated += 1

    print(f"\nCreated {generated} language page(s) in: {output_folder}")


if __name__ == "__main__":
    main()
