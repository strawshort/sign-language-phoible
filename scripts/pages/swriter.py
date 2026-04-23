import csv
import re
import subprocess
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)


def load_csv(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(csv_path, rows, fieldnames):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def show_columns(columns):
    print("\nAvailable columns:")
    for i, col in enumerate(columns, start=1):
        print(f"{i}. {col}")


def choose_one_column(columns, prompt):
    print(f"\n{prompt}")
    raw = input("> ").strip()
    return columns[int(raw) - 1]


def choose_segment_class():
    options = [
        "handshape",
        "movement",
        "location",
        "orientation",
        "non_manual_features",
    ]
    print("\nSelect the segment class for any new segments:")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    raw = input("> ").strip()
    return options[int(raw) - 1]


def find_matching_file(folder, source_code):
    folder_path = Path(folder)
    matches = sorted(folder_path.glob(f"{source_code}_*.csv"))
    if not matches:
        return None
    return matches[0]


def get_source_family(source_code):
    return source_code.split("_")[0].strip()


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


def extract_existing_segment_number(segment_id):
    match = re.match(r"seg(\d+)$", segment_id.strip())
    if not match:
        return None
    return int(match.group(1))


def next_segment_ids(existing_rows, count):
    max_num = 0
    for row in existing_rows:
        seg_id = row.get("segment_id", "").strip()
        num = extract_existing_segment_number(seg_id)
        if num is not None and num > max_num:
            max_num = num

    start = max_num + 1
    ids = [f"seg{n:05d}" for n in range(start, start + count)]
    return ids


def main():
    inventories_csv = input("Inventories CSV path: ").strip()
    segments_csv = input("Segments CSV path: ").strip()

    inventories_rows = load_csv(inventories_csv)
    segments_rows = load_csv(segments_csv)

    if not inventories_rows:
        print("Inventories CSV is empty.")
        return
    if not segments_rows:
        print("Segments CSV is empty.")
        return

    inventory_columns = list(inventories_rows[0].keys())
    segment_columns = list(segments_rows[0].keys())

    print("\n--- inventories.csv columns ---")
    show_columns(inventory_columns)
    inventory_id_column = choose_one_column(inventory_columns, "Select the inventory ID column from inventories.csv")
    data_source_column = choose_one_column(inventory_columns, "Select the data source column from inventories.csv")
    data_source_location_column = choose_one_column(inventory_columns, "Select the data source location column from inventories.csv")
    inventory_name_column = choose_one_column(inventory_columns, "Select the inventory name column from inventories.csv")

    print("\n--- segments.csv columns ---")
    show_columns(segment_columns)
    segment_id_column = choose_one_column(segment_columns, "Select the segment ID column from segments.csv")
    segment_fsw_column = choose_one_column(segment_columns, "Select the FSW column from segments.csv")
    segment_class_column = choose_one_column(segment_columns, "Select the segment class column from segments.csv")

    valid_inventories = [
        row for row in inventories_rows
        if row.get(inventory_id_column, "").strip().startswith("inv")
    ]

    if not valid_inventories:
        print("No valid inventory rows found.")
        return

    inventories_by_family = {}
    for row in valid_inventories:
        source_code = row.get(data_source_column, "").strip()
        family = get_source_family(source_code)
        inventories_by_family.setdefault(family, []).append(row)

    selected_inventories = []
    selected_families = []

    for family in sorted(inventories_by_family.keys()):
        family_rows = inventories_by_family[family]

        print(f"\n--- Source family: {family} ---")
        for i, row in enumerate(family_rows, start=1):
            source_code = row.get(data_source_column, "").strip()
            source_folder = row.get(data_source_location_column, "").strip()
            matched_file = find_matching_file(source_folder, source_code)
            matched_name = matched_file.name if matched_file else "[NO MATCHING FILE]"
            print(
                f"{i}. {row.get(inventory_id_column, '')} | "
                f"{row.get(inventory_name_column, '')} | "
                f"{source_code} | {matched_name}"
            )

        print("\nChoose inventories to process for this family:")
        print("  all = all inventories in this family")
        print("  0   = none")
        print("  1-3 = range")
        print("  1,4,7 = specific entries")
        selection = input("> ").strip().lower()

        chosen_indexes = parse_selection(selection, len(family_rows))
        if chosen_indexes:
            selected_families.append(family)
            for idx in chosen_indexes:
                selected_inventories.append(family_rows[idx])

    if not selected_inventories:
        print("No inventories selected.")
        return

    print("\n--- Inventories being processed ---")
    for row in selected_inventories:
        source_code = row.get(data_source_column, "").strip()
        source_folder = row.get(data_source_location_column, "").strip()
        matched_file = find_matching_file(source_folder, source_code)
        matched_name = matched_file.name if matched_file else "[NO MATCHING FILE]"
        print(
            f"{row.get(inventory_id_column, '')} | "
            f"{row.get(inventory_name_column, '')} | "
            f"{source_code} | {matched_name}"
        )

    proceed = input("\nProceed with these inventories? (y/n): ").strip().lower()
    if proceed != "y":
        print("Cancelled.")
        return

    family_fsw_columns = {}

    for family in selected_families:
        family_rows = [row for row in selected_inventories if get_source_family(row.get(data_source_column, "").strip()) == family]
        sample_row = family_rows[0]
        sample_file = find_matching_file(
            sample_row.get(data_source_location_column, "").strip(),
            sample_row.get(data_source_column, "").strip(),
        )

        if not sample_file:
            print(f"Skipping family {family}: no matching sample file found.")
            continue

        sample_rows = load_csv(sample_file)
        if not sample_rows:
            print(f"Skipping family {family}: sample file is empty.")
            continue

        source_columns = list(sample_rows[0].keys())

        print(f"\n--- Columns for source family: {family} ---")
        show_columns(source_columns)
        family_fsw_columns[family] = choose_one_column(
            source_columns,
            f"Select the FSW column for all {family} source files",
        )

    segment_class_value = choose_segment_class()

    existing_fsw_values = {
        row.get(segment_fsw_column, "").strip()
        for row in segments_rows
        if row.get(segment_fsw_column, "").strip()
    }

    found_fsw_values = set()

    for row in selected_inventories:
        source_code = row.get(data_source_column, "").strip()
        source_folder = row.get(data_source_location_column, "").strip()
        family = get_source_family(source_code)

        source_file = find_matching_file(source_folder, source_code)
        if not source_file:
            print(f"Skipping {row.get(inventory_id_column, '')}: no matching file found.")
            continue

        if family not in family_fsw_columns:
            print(f"Skipping {row.get(inventory_id_column, '')}: no FSW column selected for family {family}.")
            continue

        source_rows = load_csv(source_file)
        source_fsw_column = family_fsw_columns[family]

        for source_row in source_rows:
            fsw_value = source_row.get(source_fsw_column, "").strip()
            if fsw_value:
                found_fsw_values.add(fsw_value)

    new_fsw_values = sorted(fsw for fsw in found_fsw_values if fsw not in existing_fsw_values)

    current_segment_count = len(segments_rows)
    new_segment_count = len(new_fsw_values)

    if new_segment_count == 0:
        print("\nNo new FSW values found. segments.csv does not need updating.")
        run_generator = input("Do you still want to run generator.py? (y/n): ").strip().lower()
        if run_generator == "y":
            subprocess.run([sys.executable, "scripts/pages/generator.py"])
        return

    new_ids = next_segment_ids(segments_rows, new_segment_count)

    print("\n--- Summary before writing ---")
    print(f"Current number of rows in segments.csv: {current_segment_count}")
    print(f"Number of unique new FSW values found: {new_segment_count}")
    print(f"New segment IDs will run from: {new_ids[0]} to {new_ids[-1]}")

    preview_count = min(10, len(new_fsw_values))
    print(f"\nFirst {preview_count} new FSW values:")
    for fsw in new_fsw_values[:preview_count]:
        print(f"  {fsw}")

    confirm_write = input("\nWrite these new rows to segments.csv? (y/n): ").strip().lower()
    if confirm_write != "y":
        print("Cancelled. No changes written.")
        return

    for new_id, fsw_value in zip(new_ids, new_fsw_values):
        new_row = {col: "" for col in segment_columns}
        new_row[segment_id_column] = new_id
        new_row[segment_fsw_column] = fsw_value
        new_row[segment_class_column] = segment_class_value
        segments_rows.append(new_row)

    write_csv(segments_csv, segments_rows, segment_columns)

    print(f"\nAdded {new_segment_count} new rows to {segments_csv}.")

    run_generator = input("Do you want to run generator.py now? (y/n): ").strip().lower()
    if run_generator == "y":
        subprocess.run([sys.executable, "scripts/pages/generator.py"])
    else:
        print("Remember to run generator.py manually.")


if __name__ == "__main__":
    main()
