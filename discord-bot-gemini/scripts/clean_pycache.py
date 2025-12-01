#!/usr/bin/env python3
"""
Cache Cleaner Script
Cleans Python cache files and directories (__pycache__, *.pyc, *.pyo)
"""

import os
import shutil
import sys
from pathlib import Path


def clean_pycache(root_dir: str = ".") -> None:
    """
    Recursively clean Python cache files and directories.

    Args:
        root_dir: Root directory to start cleaning from (default: current directory)
    """
    root_path = Path(root_dir).resolve()
    cleaned_items = []

    print(f"🧹 Cleaning Python cache files in: {root_path}")
    print("-" * 50)

    # Walk through all directories
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_path = Path(dirpath)

        # Remove __pycache__ directories
        if "__pycache__" in dirnames:
            pycache_path = current_path / "__pycache__"
            try:
                shutil.rmtree(pycache_path)
                cleaned_items.append(f"Removed directory: {pycache_path}")
                dirnames.remove("__pycache__")  # Prevent walking into deleted directory
            except Exception as e:
                print(f"❌ Error removing {pycache_path}: {e}")

        # Remove .pyc and .pyo files
        for filename in filenames:
            if filename.endswith(('.pyc', '.pyo')):
                file_path = current_path / filename
                try:
                    file_path.unlink()
                    cleaned_items.append(f"Removed file: {file_path}")
                except Exception as e:
                    print(f"❌ Error removing {file_path}: {e}")

    # Summary
    if cleaned_items:
        print(f"✅ Cleaned {len(cleaned_items)} items:")
        for item in cleaned_items[:10]:  # Show first 10 items
            print(f"  {item}")
        if len(cleaned_items) > 10:
            print(f"  ... and {len(cleaned_items) - 10} more items")
    else:
        print("✅ No cache files found to clean")

    print("-" * 50)
    print("🧹 Cache cleaning completed!")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean Python cache files (__pycache__, *.pyc, *.pyo)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean_pycache.py                    # Clean current directory
  python clean_pycache.py /path/to/project   # Clean specific directory
  python clean_pycache.py ..                 # Clean parent directory
        """
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to clean (default: current directory)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without actually deleting"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
        print("This would clean cache files in:", Path(args.directory).resolve())
        # TODO: Implement dry run functionality
        print("Dry run not yet implemented. Use without --dry-run to actually clean.")
        return

    try:
        clean_pycache(args.directory)
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()