import csv
import html
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

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

h1,
h2 {
  margin-top: 0;
  font-size: 1.5rem;
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

.col-segment-id,
.col-segment-class,
.col-fsw,
.col-signwriting-1,
.col-signwriting-2 {
  white-space: nowrap;
}

.col-hamnosys-1-initial-configuration,
.col-hamnosys-2-basic-handshape,
.col-hamnosys-3-handshape-modifications {
  white-space: normal;
  min-width: 180px;
  max-width: 320px;
  overflow-wrap: break-word;
}

.col-inventory,
.col-language,
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


def find_column_case_insensitive(columns, target_name):
    for column in columns:
        if column.lower() == target_name.lower():
            return column

    return None


def get_default_source_segment_column(family, source_columns):
    family_defaults = {
        "LQ": "FSW",
        "SP": "Handshape",
    }

    default_column = family_defaults.get(family)

    if default_column:
        matched_column = find_column_case_insensitive(source_columns, default_column)

        if matched_column:
            return matched_column

    fallback_column = find_column_case_insensitive(source_columns, "fsw")

    if fallback_column:
        return fallback_column

    return source_columns[0]


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


def format_header(column_name):
    special_headers = {
        "fsw": "FSW",
        "hamnosys_1_initial_configuration": "HamNoSys 1<br><span>Initial Configuration</span>",
        "hamnosys_2_basic_handshape": "HamNoSys 2<br><span>Basic Handshape</span>",
        "hamnosys_3_handshape_modifications": "HamNoSys 3<br><span>Handshape Modifications</span>",
    }

    if column_name in special_headers:
        return special_headers[column_name]

    return html.escape(column_name.replace("_", " ").title())


def format_cell_value(value):
    value = str(value).strip()

    if value == "":
        return '<span class="empty-cell">—</span>'

    return html.escape(value)


def column_class_name(column_name):
    return f"col-{column_name.replace('_', '-').lower()}"


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


def render_segment_details(segment_row, columns_to_show):
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
        value = format_cell_value(segment_row.get(col, ""))
        column_class = column_class_name(col)

        if col.startswith("signwriting"):
            parts.append(f'<td class="signwriting {column_class}">{value}</td>')
        else:
            parts.append(f'<td class="{column_class}">{value}</td>')

    parts.append("</tr></tbody>")
    parts.append("</table>")
    parts.append("</div>")

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
    parts.append(render_search_box())
    parts.append('<div class="table-container">')
    parts.append('<table class="filterable-table">')
    parts.append("<thead><tr>")
    parts.append('<th class="col-inventory">Inventory</th>')
    parts.append('<th class="col-language">Language</th>')
    parts.append('<th class="col-source">Source</th>')
    parts.append("</tr></thead>")
    parts.append("<tbody>")

    for row in matching_inventories:
        inv_id = row.get(inventory_id_column, "").strip()
        inv_name = row.get(inventory_name_column, "").strip()
        language = row.get(language_name_column, "").strip()
        source = row.get(source_label_column, "").strip()

        link = f"../inventories/{inv_id}.html"

        parts.append("<tr>")
        parts.append(f'<td class="col-inventory"><a href="{html.escape(link)}">{format_cell_value(inv_name)}</a></td>')
        parts.append(f'<td class="col-language">{format_cell_value(language)}</td>')
        parts.append(f'<td class="col-source">{format_cell_value(source)}</td>')
        parts.append("</tr>")

    parts.append("</tbody></table>")
    parts.append("</div>")

    return "\n".join(parts)


def write_segment_page(output_path, title, details_html, inventory_table_html):
    description = "This page lists the details for a single segment and the inventories that contain it."

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Segment: {html.escape(title)}</title>
  {PAGE_CSS}
</head>
<body>
  <main class="page">
    {render_site_nav()}

    <section class="content-card">
      <h1>Segment: {html.escape(title)}</h1>
      {details_html}
      <p class="page-description">{html.escape(description)}</p>
    </section>

    <section class="content-card">
      <h2>Inventories Containing This Segment</h2>
      {inventory_table_html}
    </section>
  </main>
  {TABLE_FILTER_SCRIPT}
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
            "output_folder": "docs/segments",
            "segment_id_column": "segment_id",
            "segment_fsw_column": "fsw",
            "segment_class_column": "segment_class",
            "segment_detail_columns": [
                "segment_id",
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


def get_settings_from_defaults(segment_columns, inventory_columns, defaults):
    print("\nDetected known CSV files.")
    print("Press Enter to keep each default, or type a replacement value.")

    output_folder = prompt_with_default(
        "Output folder for segment pages",
        defaults["output_folder"],
    )

    print("\n--- segments.csv columns ---")
    show_columns(segment_columns)

    segment_id_column = prompt_column_with_default(
        segment_columns,
        "Segment ID column from segments.csv",
        defaults["segment_id_column"],
    )

    segment_fsw_column = prompt_column_with_default(
        segment_columns,
        "FSW column from segments.csv",
        defaults["segment_fsw_column"],
    )

    segment_class_column = prompt_column_with_default(
        segment_columns,
        "Segment class column from segments.csv",
        defaults["segment_class_column"],
    )

    segment_detail_columns = prompt_columns_with_default(
        segment_columns,
        "Columns to show in the segment details table",
        defaults["segment_detail_columns"],
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

    language_name_column = prompt_column_with_default(
        inventory_columns,
        "Language name column from inventories.csv",
        defaults["language_name_column"],
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

    data_source_column = prompt_column_with_default(
        inventory_columns,
        "Data source column from inventories.csv",
        defaults["data_source_column"],
    )

    data_source_location_column = prompt_column_with_default(
        inventory_columns,
        "Data source location column from inventories.csv",
        defaults["data_source_location_column"],
    )

    return {
        "output_folder": output_folder,
        "segment_id_column": segment_id_column,
        "segment_fsw_column": segment_fsw_column,
        "segment_class_column": segment_class_column,
        "segment_detail_columns": segment_detail_columns,
        "inventory_id_column": inventory_id_column,
        "inventory_name_column": inventory_name_column,
        "language_name_column": language_name_column,
        "contributor_column": contributor_column,
        "year_column": year_column,
        "data_source_column": data_source_column,
        "data_source_location_column": data_source_location_column,
    }


def choose_known_csv_paths():
    segments_csv = prompt_with_default(
        "Segments CSV path",
        "data/slphoible/segments.csv",
    )

    inventories_csv = prompt_with_default(
        "Inventories CSV path",
        "data/slphoible/inventories.csv",
    )

    return segments_csv, inventories_csv


def main():
    print()
    print("This program creates individual segment HTML pages from segments.csv.")
    print("Each segment page shows the segment details and the inventories that contain that segment.")

    segments_csv, inventories_csv = choose_known_csv_paths()

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

    if not defaults:
        print("\nNo defaults found for the selected CSV files.")
        print("Add these CSV files to get_known_defaults() before generating segment pages.")
        return

    settings = get_settings_from_defaults(
        segment_columns=segment_columns,
        inventory_columns=inventory_columns,
        defaults=defaults,
    )

    output_folder = settings["output_folder"]
    segment_id_column = settings["segment_id_column"]
    segment_fsw_column = settings["segment_fsw_column"]
    segment_class_column = settings["segment_class_column"]
    segment_detail_columns = settings["segment_detail_columns"]
    inventory_id_column = settings["inventory_id_column"]
    inventory_name_column = settings["inventory_name_column"]
    language_name_column = settings["language_name_column"]
    contributor_column = settings["contributor_column"]
    year_column = settings["year_column"]
    data_source_column = settings["data_source_column"]
    data_source_location_column = settings["data_source_location_column"]

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

    family_segment_columns = {}

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

        default_source_segment_column = get_default_source_segment_column(
            family,
            source_columns,
        )

        family_segment_columns[family] = prompt_column_with_default(
            source_columns,
            f"Source column containing segment values for all {family} source files",
            default_source_segment_column,
        )

    inventory_segment_lookup = {}

    print("\nScanning inventory files...")

    for inv in valid_inventories:
        source_code = inv.get(data_source_column, "").strip()
        source_folder = inv.get(data_source_location_column, "").strip()
        family = get_source_family(source_code)

        source_file = find_matching_file(source_folder, source_code)

        if not source_file:
            continue

        if family not in family_segment_columns:
            continue

        source_rows = load_csv(source_file)
        source_segment_column = family_segment_columns[family]

        segment_values = {
            row.get(source_segment_column, "").strip()
            for row in source_rows
            if row.get(source_segment_column, "").strip() != ""
        }

        inventory_segment_lookup[inv.get(inventory_id_column, "")] = segment_values

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
            inv_segment_values = inventory_segment_lookup.get(inv_id, set())

            if segment_fsw in inv_segment_values:
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
