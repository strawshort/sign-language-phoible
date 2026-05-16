import csv
import html
from pathlib import Path
import sys

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

.page-description em {
  color: #555;
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

.metadata-table .col-inventory-id {
  white-space: nowrap;
}

.metadata-table .col-language-name,
.metadata-table .col-contributor {
  white-space: normal;
  max-width: 420px;
  overflow-wrap: break-word;
}

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


def prompt_columns_with_default(columns, label, default_columns, allow_none=False):
    default_text = format_columns_with_numbers(columns, default_columns)

    if allow_none:
        raw = input(
            f"\n{label} [{default_text}] (Enter = default, type numbers, or 0 for none): "
        ).strip()
    else:
        raw = input(
            f"\n{label} [{default_text}] (Enter = default, or type numbers): "
        ).strip()

    if raw == "":
        return default_columns

    if allow_none and raw == "0":
        return []

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


def join_inventory_rows(source_rows, source_segment_column, segments_lookup, segment_columns_to_add):
    joined = []

    for row in source_rows:
        segment_value = row.get(source_segment_column, "").strip()
        segment_row = segments_lookup.get(segment_value, {})

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


def render_table(rows, columns_to_show, fsw_column):
    parts = []
    parts.append(render_search_box())
    parts.append('<div class="table-container">')
    parts.append('<table class="filterable-table">')
    parts.append("<thead><tr>")

    for col in columns_to_show:
        column_class = column_class_name(col)
        parts.append(f'<th class="{column_class}">{format_header(col)}</th>')

    parts.append("</tr></thead>")
    parts.append("<tbody>")

    for row in rows:
        parts.append("<tr>")

        for col in columns_to_show:
            value = row.get(col, "").strip()
            column_class = column_class_name(col)

            if col == fsw_column:
                cell = build_fsw_link(value, row.get("segment_id", ""))
            else:
                cell = format_cell_value(value)

            if col.startswith("signwriting"):
                parts.append(f'<td class="signwriting {column_class}">{cell}</td>')
            else:
                parts.append(f'<td class="{column_class}">{cell}</td>')

        parts.append("</tr>")

    parts.append("</tbody></table>")
    parts.append("</div>")

    return "\n".join(parts)


def render_inventory_metadata(inventory_row):
    wanted = [
        "inventory_id",
        "language_name",
        "contributor",
    ]

    columns_to_show = [
        key for key in wanted
        if key in inventory_row
    ]

    parts = []
    parts.append('<div class="metadata-table-container">')
    parts.append('<table class="metadata-table">')
    parts.append("<thead><tr>")

    for key in columns_to_show:
        column_class = column_class_name(key)
        parts.append(f'<th class="{column_class}">{format_header(key)}</th>')

    parts.append("</tr></thead>")
    parts.append("<tbody><tr>")

    for key in columns_to_show:
        value = inventory_row.get(key, "").strip()
        column_class = column_class_name(key)
        parts.append(f'<td class="{column_class}">{format_cell_value(value)}</td>')

    parts.append("</tr></tbody>")
    parts.append("</table>")
    parts.append("</div>")

    return "\n".join(parts)


def write_inventory_page(output_path, title, metadata_html, table_html):
    description = "This page lists the segments associated with a single inventory."
    data_note = "The dataset is derived from the cited source, and the repository does not independently evaluate or correct the original data. As a result, extracted inventories may retain source-level inconsistencies or errors."

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Inventory: {html.escape(title)}</title>
  {PAGE_CSS}
</head>
<body>
  <main class="page">
    {render_site_nav()}

    <section class="content-card">
      <h1>Inventory: {html.escape(title)}</h1>
      {metadata_html}
      <p class="page-description">
        {html.escape(description)}
        <em><strong>Data note:</strong> {html.escape(data_note)}</em>
      </p>
    </section>

    <section class="content-card">
      <h2>Segments</h2>
      {table_html}
    </section>
  </main>
  {TABLE_FILTER_SCRIPT}
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
            "output_folder": "docs/inventories",
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
        source_segment_column = family_configs[family]["source_segment_column"]

        for row in source_rows:
            segment_value = row.get(source_segment_column, "").strip()

            if segment_value and segment_value not in segments_lookup:
                missing_fsws.add(segment_value)

    return sorted(missing_fsws)


def compress_number_ranges(numbers):
    if not numbers:
        return ""

    numbers = sorted(numbers)
    ranges = []
    start = numbers[0]
    previous = numbers[0]

    for number in numbers[1:]:
        if number == previous + 1:
            previous = number
        else:
            if start == previous:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{previous}")

            start = number
            previous = number

    if start == previous:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{previous}")

    return ", ".join(ranges)


def print_inventory_page_options(valid_inventories, source_file_column):
    family_numbers = {}

    for index, inventory in enumerate(valid_inventories, start=1):
        source_code = inventory[source_file_column].strip()
        family = get_source_family(source_code)

        if family not in family_numbers:
            family_numbers[family] = []

        family_numbers[family].append(index)

    print("\nAvailable inventory pages:")

    for family, numbers in family_numbers.items():
        print(f"- {family}: {compress_number_ranges(numbers)}")


def parse_inventory_selection(selection, valid_inventories, source_file_column):
    selection = selection.strip()

    if selection == "" or selection.lower() == "all":
        return valid_inventories

    family_numbers = {}

    for index, inventory in enumerate(valid_inventories, start=1):
        family = get_source_family(inventory[source_file_column].strip())

        if family not in family_numbers:
            family_numbers[family] = set()

        family_numbers[family].add(index)

    selected_numbers = set()
    parts = [part.strip() for part in selection.split(",") if part.strip()]

    for part in parts:
        family = part.upper()

        if family in family_numbers:
            selected_numbers.update(family_numbers[family])
            continue

        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text.strip())
            end = int(end_text.strip())
            selected_numbers.update(range(start, end + 1))
            continue

        selected_numbers.add(int(part))

    selected_inventories = []

    for index, inventory in enumerate(valid_inventories, start=1):
        if index in selected_numbers:
            selected_inventories.append(inventory)

    return selected_inventories


def get_settings_from_defaults(segments_columns, inventories_columns, defaults):
    print("\nDetected known CSV files.")
    print("Press Enter to keep each default, or type a replacement value.")

    output_folder = prompt_with_default(
        "Output folder for inventory pages",
        defaults["output_folder"],
    )

    print("\n--- segments.csv columns ---")
    show_columns(segments_columns)

    segment_id_column = prompt_column_with_default(
        segments_columns,
        "Segment ID column from segments.csv",
        defaults["segment_id_column"],
    )

    segment_fsw_column = prompt_column_with_default(
        segments_columns,
        "FSW column from segments.csv",
        defaults["segment_fsw_column"],
    )

    segment_columns_to_add = prompt_columns_with_default(
        segments_columns,
        "Columns from segments.csv to include on all inventory pages",
        defaults["segment_columns_to_add"],
        allow_none=True,
    )

    print("\n--- inventories.csv columns ---")
    show_columns(inventories_columns)

    source_file_column = prompt_column_with_default(
        inventories_columns,
        "Data source column from inventories.csv",
        defaults["source_file_column"],
    )

    source_folder_column = prompt_column_with_default(
        inventories_columns,
        "Source folder column from inventories.csv",
        defaults["source_folder_column"],
    )

    inventory_id_column = prompt_column_with_default(
        inventories_columns,
        "Inventory ID column from inventories.csv",
        defaults["inventory_id_column"],
    )

    inventory_title_column = prompt_column_with_default(
        inventories_columns,
        "Inventory name column from inventories.csv",
        defaults["inventory_title_column"],
    )

    return {
        "output_folder": output_folder,
        "segment_id_column": segment_id_column,
        "segment_fsw_column": segment_fsw_column,
        "segment_columns_to_add": segment_columns_to_add,
        "source_file_column": source_file_column,
        "source_folder_column": source_folder_column,
        "inventory_id_column": inventory_id_column,
        "inventory_title_column": inventory_title_column,
    }


def choose_known_csv_paths():
    inventories_csv = prompt_with_default(
        "Inventories CSV path",
        "data/slphoible/inventories.csv",
    )

    segments_csv = prompt_with_default(
        "Segments CSV path",
        "data/slphoible/segments.csv",
    )

    return inventories_csv, segments_csv


def main():
    print()
    print("This program creates individual inventory HTML pages from inventories.csv.")
    print("It displays the inventory details, reads segment values from each inventory source file, and uses segments.csv to show the corresponding standardized segment information.")

    inventories_csv, segments_csv = choose_known_csv_paths()

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

    if not defaults:
        print("\nNo defaults found for the selected CSV files.")
        print("Add these CSV files to get_known_defaults() before generating inventory pages.")
        return

    settings = get_settings_from_defaults(
        segments_columns=segments_columns,
        inventories_columns=inventories_columns,
        defaults=defaults,
    )

    segment_id_column = settings["segment_id_column"]
    segment_fsw_column = settings["segment_fsw_column"]
    segment_columns_to_add = settings["segment_columns_to_add"]
    source_file_column = settings["source_file_column"]
    source_folder_column = settings["source_folder_column"]
    inventory_id_column = settings["inventory_id_column"]
    inventory_title_column = settings["inventory_title_column"]
    output_folder = settings["output_folder"]

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

    print_inventory_page_options(
        valid_inventories=valid_inventories,
        source_file_column=source_file_column,
    )

    inventory_selection = input(
        "\nWhich inventory pages do you want to generate? Enter numbers, ranges, family codes, or 'all' (for example: 1, 3, 7-12, SP, or all): "
    ).strip()

    valid_inventories = parse_inventory_selection(
        selection=inventory_selection,
        valid_inventories=valid_inventories,
        source_file_column=source_file_column,
    )

    if not valid_inventories:
        print("No inventory pages selected.")
        return

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

        default_source_segment_column = get_default_source_segment_column(
            family,
            source_columns,
        )

        source_segment_column = prompt_column_with_default(
            source_columns,
            f"Source column containing segment values for all {family} source files",
            default_source_segment_column,
        )

        family_configs[family] = {
            "source_segment_column": source_segment_column,
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
        print("\nThe following segment values were found in inventory source files but not in segments.csv:")

        for fsw in missing_fsws:
            print(f"  - {fsw}")

        print("\nPlease update segments.csv with these values before generating inventory pages.")
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
        source_segment_column = config["source_segment_column"]

        source_rows = [
            row for row in source_rows
            if row.get(source_segment_column, "").strip() != ""
        ]

        joined_rows = join_inventory_rows(
            source_rows,
            source_segment_column=source_segment_column,
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
