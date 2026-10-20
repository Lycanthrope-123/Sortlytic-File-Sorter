
import shutil
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from datetime import datetime

# ========== SETTINGS ==========
SORT_BY = "name"       # "name", "date", or "size"
DRY_RUN = True      # True = preview, False = move files

SMALL_LIMIT_MB = 10
MEDIUM_LIMIT_MB = 100
# ==============================


def choose_folder():
    """Let the user select any folder on their computer."""
    root = tk.Tk()
    root.withdraw()

    folder = filedialog.askdirectory(
        title="Select a folder to sort"
    )

    root.destroy()

    if not folder:
        print("No folder selected. Exiting.")
        return None

    return Path(folder)


def get_destination(file_path, source_folder):
    """Determine the destination based on the sorting method."""

    if SORT_BY == "name":
        # Group by file extension
        extension = file_path.suffix.lower().lstrip(".")
        folder_name = extension if extension else "No Extension"

    elif SORT_BY == "date":
        # Group by year and month last modified
        modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        folder_name = modified.strftime("%Y-%m")

    elif SORT_BY == "size":
        # Group by file size
        size_mb = file_path.stat().st_size / (1024 * 1024)

        if size_mb < SMALL_LIMIT_MB:
            folder_name = "Small"
        elif size_mb < MEDIUM_LIMIT_MB:
            folder_name = "Medium"
        else:
            folder_name = "Large"

    else:
        raise ValueError(
            "SORT_BY must be 'name', 'date', or 'size'."
        )

    return source_folder / folder_name


def unique_destination(destination):
    """Avoid overwriting existing files by choosing a new filename."""
    if not destination.exists():
        return destination

    original_name = destination.stem
    extension = destination.suffix
    parent = destination.parent
    counter = 1

    while True:
        new_destination = parent / (
            f"{original_name} ({counter}){extension}"
        )

        if not new_destination.exists():
            return new_destination

        counter += 1


def sort_files(source_folder):
    if not source_folder or not source_folder.is_dir():
        print("The selected folder is invalid.")
        return

    print(f"\nSelected folder: {source_folder}")
    print(f"Sorting method: {SORT_BY}")
    print(f"Preview mode: {DRY_RUN}\n")

    moved = 0
    skipped = 0
    errors = 0

    # Snapshot the files before creating destination folders
    files = list(source_folder.iterdir())

    for file_path in files:
        if not file_path.is_file():
            continue

        try:
            destination_folder = get_destination(
                file_path, source_folder
            )

            # Don't move a file onto itself
            if destination_folder == file_path.parent:
                skipped += 1
                continue

            destination = unique_destination(
                destination_folder / file_path.name
            )

            print(f"{file_path.name} -> {destination_folder.name}/")

            if not DRY_RUN:
                destination_folder.mkdir(
                    parents=True, exist_ok=True
                )
                shutil.move(str(file_path), str(destination))

            moved += 1

        except OSError as error:
            print(f"Could not sort {file_path.name}: {error}")
            errors += 1

    print("\n========== SUMMARY ==========")
    print(f"Files {'previewed' if DRY_RUN else 'moved'}: {moved}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")

    if DRY_RUN:
        print("\nNothing was moved.")
        print("Set DRY_RUN = False to perform the sorting.")


def main():
    print("AUTOMATIC FILE SORTER")
    print("Choose a folder in the window that opens.")

    folder = choose_folder()

    if folder is not None:
        sort_files(folder)


if __name__ == "__main__":
    main()
