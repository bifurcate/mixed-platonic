"""Export census data from a gathered data.json to CSV.

Reads the combined ``data.json`` produced by ``gather_census.py`` and
writes one row per solve environment.  Columns are fixed config fields
followed by the union of all ``info`` fields observed across
environments.  Non-scalar values are serialized as JSON.

Usage:
    poetry run python src/export_census_csv.py data/short_cusp_12
    poetry run python src/export_census_csv.py data/short_cusp_12 -o report.csv
"""

import argparse
import csv
import json
import logging
from pathlib import Path


CONFIG_COLUMNS = ["name", "num_tets", "num_octs", "pattern", "pattern_type"]


def load_census_data(census_path: Path) -> dict:
    with open(census_path / "data.json", "r") as f:
        return json.load(f)


def collect_info_columns(census_data: dict) -> list[str]:
    """Return the sorted union of all info field names across environments."""
    keys: set[str] = set()
    for env_data in census_data.values():
        info = env_data.get("info") or {}
        keys.update(info.keys())
    return sorted(keys)


def format_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value if isinstance(value, str) else str(value)
    return json.dumps(value, separators=(",", ":"))


def build_row(env_name: str, env_data: dict, info_columns: list[str]) -> dict:
    config = env_data.get("config") or {}
    info = env_data.get("info") or {}
    row = {"name": config.get("name", env_name)}
    for key in CONFIG_COLUMNS[1:]:
        row[key] = format_value(config.get(key))
    for key in info_columns:
        row[key] = format_value(info.get(key))
    return row


def export_csv(census_data: dict, output_path: Path) -> int:
    info_columns = collect_info_columns(census_data)
    fieldnames = CONFIG_COLUMNS + info_columns

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for env_name in sorted(census_data.keys()):
            writer.writerow(build_row(env_name, census_data[env_name], info_columns))
    return len(census_data)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="MP-CSV|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Export census data from a gathered data.json to CSV"
    )
    parser.add_argument(
        "census_dir",
        type=str,
        help="Path to the census root directory (must contain data.json)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output CSV path (default: <census_dir>/census.csv)",
    )

    args = parser.parse_args()
    census_path = Path(args.census_dir)

    if not census_path.is_dir():
        logging.error(f"Census directory not found: {census_path}")
        exit(1)

    data_path = census_path / "data.json"
    if not data_path.is_file():
        logging.error(f"No data.json found in {census_path}. Run gather_census.py first.")
        exit(1)

    census_data = load_census_data(census_path)
    output_path = Path(args.output) if args.output else census_path / "census.csv"
    n = export_csv(census_data, output_path)
    logging.info(f"Wrote {n} rows -> {output_path}")


if __name__ == "__main__":
    main()
