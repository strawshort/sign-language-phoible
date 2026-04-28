import csv
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


def choose_actions():
    print("\nChoose what you want to do in inventories.csv.")
    print("You can choose one or more options, separated by commas (for example: 1,2 or 1,2,3).")
    print()
    print("1 = Run a language-name cross-check")
    print("    * compares language_name in inventories.csv and languages.csv")
    print("    * reports names that do not match in either direction")
    print("    * for each name in inventories.csv that is not found in languages.csv, offers the option to replace it")
    print("    * if you choose to replace it, asks you to enter a language name exactly as it appears in languages.csv")
    print("    * repeats the check until a valid replacement is confirmed or you choose not to replace it")
    print("    * if a name is found in inventories.csv but not in languages.csv, flags it for review")
    print()
    print("2 = Generate inventory_name")
    print("    * pulls language_abbreviation from languages.csv")
    print("    * combines it with data_source from inventories.csv")
    print("    * writes inventory_name as: language_abbreviation (data_source)")
    print()
    print("3 = Update inventory counts")
    print("    * updates one ct_ count column from the inventory files")
    print("    * for example: ct_handshapes")
    print("    * automatically recalculates ct_segments as the total")
    print()
    print("After completing any selected updates, the script can offer to run generator.py to regenerate inventories.html.")

    raw = input("\nEnter your choices: ").strip()
    actions = set()

    for part in raw.split(","):
        part = part.strip()
        if part in {"1", "2", "3"}:
            actions.add(part)

    return actions


def get_known_defaults(inventories_csv=None, languages_csv=None):
    defaults = {}

    if inventories_csv:
        inv_norm = str(Path(inventories_csv)).replace("\\", "/").lower()
        if Path(inventories_csv).name.startswith("inventories") and Path(inventories_csv).suffix == ".csv":
            defaults.update({
                "inventory_id_column": "inventory_id",
                "inventory_name_column": "inventory_name",
                "inventory_language_name_column": "language_name",
                "data_source_column": "data_source",
                "data_source_location_column": "data_source_location",
                "count_target_column": "ct_handshapes",
            })

    if languages_csv:
        lang_norm = str(Path(languages_csv)).replace("\\", "/").lower()
        if Path(languages_csv).name.startswith("languages") and Path(languages_csv).suffix == ".csv":
            defaults.update({
                "language_name_column": "language_name",
                "language_abbreviation_column": "language_abbreviation",
            })

    return defaults if defaults else None


def get_source_family(source_code):
    return source_code.split("_")[0].strip()


def find_matching_file(folder, source_code):
    folder_path = Path(folder)
    matches = sorted(folder_path.glob(f"{source_code}_*.csv"))
    if not matches:
        return None
    return matches[0]


def count_non_empty_fsw_rows(source_file, fsw_column):
    rows = load_csv(source_file)
    return sum(1 for row in rows if row.get(fsw_column, "").strip() != "")


def safe_int(value):
    value = str(value).strip()
    if value == "":
        return 0
    return int(value)


def recompute_ct_segments(row, count_columns, ct_segments_column):
    total = 0
    for col in count_columns:
        if col == ct_segments_column:
            continue
        total += safe_int(row.get(col, ""))
    row[ct_segments_column] = str(total)


def build_language_lookup(languages_rows, language_name_column):
    return {
        row.get(language_name_column, "").strip(): row
        for row in languages_rows
        if row.get(language_name_column, "").strip()
    }


def select_inventories_by_family(
    valid_inventories,
    inventory_id_column,
    inventory_name_column,
    data_source_column,
    data_source_location_column,
    header_message,
):
    print(f"\n{header_message}")

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

    return selected_inventories, selected_families


def run_language_cross_check(
    valid_inventories,
    languages_rows,
    inventory_language_name_column,
    language_name_column,
):
    language_lookup = build_language_lookup(languages_rows, language_name_column)

    inventory_language_names = {
        row.get(inventory_language_name_column, "").strip()
        for row in valid_inventories
        if row.get(inventory_language_name_column, "").strip()
    }

    languages_language_names = set(language_lookup.keys())

    inventory_only = sorted(inventory_language_names - languages_language_names)
    languages_only = sorted(languages_language_names - inventory_language_names)

    print("\n--- Language-name cross-check ---")

    if inventory_only:
        print("\nFound in inventories.csv but not in languages.csv:")
        for name in inventory_only:
            print(f"  - {name}")
    else:
        print("\nAll language_name values in inventories.csv were found in languages.csv.")

    if languages_only:
        print("\nFound in languages.csv but not in inventories.csv:")
        for name in languages_only:
            print(f"  - {name}")
    else:
        print("\nAll language_name values in languages.csv were found in inventories.csv.")

    replacements = {}

    for old_name in inventory_only:
        while True:
            print(f"\nThe following language_name in inventories.csv was not found in languages.csv:")
            print(f"  {old_name}")

            while True:
                replace = input("\nWould you like to replace it? (y/n): ").strip().lower()
                if replace in {"y", "n"}:
                    break
                print("Please enter only 'y' or 'n'.")

            if replace == "n":
                print(f"Please check whether '{old_name}' needs to be added to languages.csv.")
                break

            new_name = input(
                "Enter the replacement language_name exactly as it appears in languages.csv: "
            ).strip()

            if new_name == "":
                print("No replacement entered.")
                continue

            if new_name not in language_lookup:
                print("\nThat language_name was not found in languages.csv.")
                continue

            confirm = input(
                f"Replace '{old_name}' with '{new_name}' in inventories.csv? (y/n): "
            ).strip().lower()

            if confirm == "y":
                replacements[old_name] = new_name
                break

    if replacements:
        print("\nApplying selected language_name replacements in inventories.csv...")
        for row in valid_inventories:
            current_name = row.get(inventory_language_name_column, "").strip()
            if current_name in replacements:
                row[inventory_language_name_column] = replacements[current_name]

    return bool(replacements)


def regenerate_inventory_names(
    selected_inventories,
    language_lookup,
    inventory_id_column,
    inventory_language_name_column,
    language_abbreviation_column,
    data_source_column,
    inventory_name_column,
):
    changed = 0
    skipped = []

    for row in selected_inventories:
        language_name = row.get(inventory_language_name_column, "").strip()
        data_source = row.get(data_source_column, "").strip()

        if language_name not in language_lookup:
            skipped.append((row.get(inventory_id_column, ""), language_name))
            continue

        language_row = language_lookup[language_name]
        language_abbreviation = language_row.get(language_abbreviation_column, "").strip()

        if not language_abbreviation:
            skipped.append((row.get(inventory_id_column, ""), language_name))
            continue

        new_inventory_name = f"{language_abbreviation} ({data_source})"
        if row.get(inventory_name_column, "") != new_inventory_name:
            row[inventory_name_column] = new_inventory_name
            changed += 1

    if skipped:
        print("\nSkipped inventory_name updates for the following inventories because no matching language_abbreviation was found:")
        for inv_id, language_name in skipped:
            print(f"  {inv_id} | {language_name}")

    return changed


def update_inventory_counts(
    selected_inventories,
    selected_families,
    data_source_column,
    data_source_location_column,
    inventory_id_column,
    inventory_name_column,
    count_target_column,
    inventory_columns,
):
    family_fsw_columns = {}

    for family in selected_families:
        family_rows = [
            row for row in selected_inventories
            if get_source_family(row.get(data_source_column, "").strip()) == family
        ]
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

    updates = []

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

        fsw_column = family_fsw_columns[family]
        count_value = count_non_empty_fsw_rows(source_file, fsw_column)

        updates.append({
            "inventory_id": row.get(inventory_id_column, ""),
            "inventory_name": row.get(inventory_name_column, ""),
            "old_value": row.get(count_target_column, ""),
            "new_value": str(count_value),
        })

    if not updates:
        print("\nNo inventory counts to update.")
        return 0

    ct_segments_column = "ct_segments"
    count_columns = [col for col in inventory_columns if col.startswith("ct_")]

    print("\n--- Summary before writing counts ---")
    print(f"Target count column: {count_target_column}")
    print(f"Inventories selected: {len(selected_inventories)}")
    print(f"Inventories with computed updates: {len(updates)}")
    if ct_segments_column in inventory_columns:
        print("ct_segments will also be recalculated as the sum of all ct_ columns.")

    preview_count = min(10, len(updates))
    print(f"\nFirst {preview_count} updates:")
    for item in updates[:preview_count]:
        print(
            f"{item['inventory_id']} | {item['inventory_name']} | "
            f"{item['old_value']} -> {item['new_value']}"
        )

    confirm_write = input("\nApply these count updates? (y/n): ").strip().lower()
    if confirm_write != "y":
        print("Cancelled count updates.")
        return 0

    updates_by_id = {item["inventory_id"]: item["new_value"] for item in updates}

    for row in selected_inventories:
        inv_id = row.get(inventory_id_column, "")
        if inv_id in updates_by_id:
            row[count_target_column] = updates_by_id[inv_id]
            if ct_segments_column in inventory_columns:
                recompute_ct_segments(row, count_columns, ct_segments_column)

    return len(updates)


def main():
    print()
    print("This program updates inventories.csv.")
    print("It ross-checks language names with languages.csv, generates inventory names, and updates inventory counts.")

    actions = choose_actions()
    if not actions:
        print("No valid actions selected.")
        return

    inventories_csv = input(
        "\nEnter the path to the inventories CSV "
        "(for example: data/slphoible/inventories.csv): "
    ).strip()

    inventories_rows = load_csv(inventories_csv)
    if not inventories_rows:
        print("Inventories CSV is empty.")
        return

    languages_csv = None
    languages_rows = None
    if "1" in actions or "2" in actions:
        languages_csv = input(
            "Enter the path to the languages CSV "
            "(for example: data/slphoible/languages.csv): "
        ).strip()

        languages_rows = load_csv(languages_csv)
        if not languages_rows:
            print("Languages CSV is empty.")
            return

    inventory_columns = list(inventories_rows[0].keys())
    language_columns = list(languages_rows[0].keys()) if languages_rows else []
    defaults = get_known_defaults(inventories_csv, languages_csv)

    print("\n--- inventories.csv columns ---")
    show_columns(inventory_columns)

    if defaults and "inventory_id_column" in defaults:
        print("\nSuggested defaults from inventories.csv:")
        if "inventory_id_column" in defaults:
            print(f"  Inventory ID column: {defaults['inventory_id_column']}")
        if "inventory_name_column" in defaults:
            print(f"  Inventory name column: {defaults['inventory_name_column']}")
        if "inventory_language_name_column" in defaults:
            print(f"  Language name column: {defaults['inventory_language_name_column']}")
        if "data_source_column" in defaults:
            print(f"  Data source column: {defaults['data_source_column']}")
        if "data_source_location_column" in defaults:
            print(f"  Data source location column: {defaults['data_source_location_column']}")
        if "3" in actions and "count_target_column" in defaults:
            print(f"  Suggested ct_ count column: {defaults['count_target_column']}")

    use_inventory_defaults = "n"
    if defaults and "inventory_id_column" in defaults:
        use_inventory_defaults = input("\nUse these inventories.csv defaults? (y/n): ").strip().lower()

    if use_inventory_defaults == "y":
        inventory_id_column = defaults["inventory_id_column"]
        inventory_name_column = defaults["inventory_name_column"]
        inventory_language_name_column = defaults["inventory_language_name_column"]
        data_source_column = defaults["data_source_column"]
        data_source_location_column = defaults["data_source_location_column"]
        count_target_column = defaults["count_target_column"] if "3" in actions else None
    else:
        inventory_id_column = choose_one_column(inventory_columns, "Select the inventory ID column from inventories.csv")
        inventory_name_column = choose_one_column(inventory_columns, "Select the inventory name column from inventories.csv")
        inventory_language_name_column = choose_one_column(inventory_columns, "Select the language name column from inventories.csv")
        data_source_column = choose_one_column(inventory_columns, "Select the data source column from inventories.csv")
        data_source_location_column = choose_one_column(inventory_columns, "Select the data source location column from inventories.csv")
        count_target_column = None


    if "3" in actions and count_target_column is None:
        count_target_column = choose_one_column(
            inventory_columns,
            "Select the count column to update from the inventory files "
            "(for example: ct_handshapes). ct_segments will be recalculated automatically.",
        )

    if languages_rows:
        print("\n--- languages.csv columns ---")
        show_columns(language_columns)

        if defaults and "language_name_column" in defaults:
            print("\nSuggested defaults from languages.csv:")
            print(f"  Language name column: {defaults['language_name_column']}")
            print(f"  Language abbreviation column: {defaults['language_abbreviation_column']}")

        use_language_defaults = "n"
        if defaults and "language_name_column" in defaults:
            use_language_defaults = input("\nUse these languages.csv defaults? (y/n): ").strip().lower()

        if use_language_defaults == "y":
            language_name_column = defaults["language_name_column"]
            language_abbreviation_column = defaults["language_abbreviation_column"]
        else:
            language_name_column = choose_one_column(language_columns, "Select the language name column from languages.csv")
            language_abbreviation_column = choose_one_column(language_columns, "Select the language abbreviation column from languages.csv")
    else:
        language_name_column = None
        language_abbreviation_column = None

    valid_inventories = [
        row for row in inventories_rows
        if row.get(inventory_id_column, "").strip().startswith("inv")
    ]

    if not valid_inventories:
        print("No valid inventory rows found.")
        return

    changed_anything = False

    if "1" in actions or "2" in actions:
        changed = run_language_cross_check(
            valid_inventories=valid_inventories,
            languages_rows=languages_rows,
            inventory_language_name_column=inventory_language_name_column,
            language_name_column=language_name_column,
        )
        changed_anything = changed_anything or changed

    language_lookup = build_language_lookup(languages_rows, language_name_column) if languages_rows else {}

    if "2" in actions:
        selected_inventories, _ = select_inventories_by_family(
            valid_inventories=valid_inventories,
            inventory_id_column=inventory_id_column,
            inventory_name_column=inventory_name_column,
            data_source_column=data_source_column,
            data_source_location_column=data_source_location_column,
            header_message="Select which inventories you want to name or rename.",
        )

        if selected_inventories:
            print("\n--- Inventories selected for inventory_name generation ---")
            for row in selected_inventories:
                inv_id = row.get(inventory_id_column, "").strip()
                old_name = row.get(inventory_name_column, "").strip()
                language_name = row.get(inventory_language_name_column, "").strip()
                data_source = row.get(data_source_column, "").strip()

                if language_name in language_lookup:
                    language_row = language_lookup[language_name]
                    abbreviation = language_row.get(language_abbreviation_column, "").strip()
                    if abbreviation:
                        new_name = f"{abbreviation} ({data_source})"
                    else:
                        new_name = "[NO MATCHING language_abbreviation]"
                else:
                    new_name = "[NO MATCHING language_name]"

                print(f"{inv_id} | {old_name} | {language_name} -> {new_name}")

            confirm = input("\nGenerate inventory_name for these inventories? (y/n): ").strip().lower()
            if confirm == "y":
                changed_count = regenerate_inventory_names(
                    selected_inventories=selected_inventories,
                    language_lookup=language_lookup,
                    inventory_id_column=inventory_id_column,
                    inventory_language_name_column=inventory_language_name_column,
                    language_abbreviation_column=language_abbreviation_column,
                    data_source_column=data_source_column,
                    inventory_name_column=inventory_name_column,
                )
                print(f"\nUpdated inventory_name for {changed_count} inventory row(s).")
                changed_anything = changed_anything or (changed_count > 0)
            else:
                print("Skipped inventory_name generation.")
        else:
            print("No inventories selected for inventory_name generation.")

    if "3" in actions:
        selected_inventories, selected_families = select_inventories_by_family(
            valid_inventories=valid_inventories,
            inventory_id_column=inventory_id_column,
            inventory_name_column=inventory_name_column,
            data_source_column=data_source_column,
            data_source_location_column=data_source_location_column,
            header_message="Select which inventories you want to count or recount.",
        )

        if selected_inventories:
            count_updates = update_inventory_counts(
                selected_inventories=selected_inventories,
                selected_families=selected_families,
                data_source_column=data_source_column,
                data_source_location_column=data_source_location_column,
                inventory_id_column=inventory_id_column,
                inventory_name_column=inventory_name_column,
                count_target_column=count_target_column,
                inventory_columns=inventory_columns,
            )
            if count_updates > 0:
                print(f"\nUpdated counts for {count_updates} inventory row(s).")
                changed_anything = True
        else:
            print("No inventories selected for count updates.")

    if not changed_anything:
        print("\nNo changes to write.")
        return

    write_csv(inventories_csv, inventories_rows, inventory_columns)
    print(f"\nSaved updates to {inventories_csv}.")

    run_generator = input(
        "Do you want to run generator.py now to regenerate inventories.html? (y/n): "
    ).strip().lower()

    if run_generator == "y":
        subprocess.run([sys.executable, "scripts/pages/generator.py"])
    else:
        print("Remember to run generator.py manually.")


if __name__ == "__main__":
    main()
