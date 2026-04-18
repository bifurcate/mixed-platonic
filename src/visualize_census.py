"""Visualize census data from a gathered data.json.

Reads the combined ``data.json`` produced by ``gather_census.py`` and
generates charts as a multi-page PDF.  Only environments that have an
``info`` section (i.e. completed or in-progress solves) are included
in plots that depend on solver metrics.

Usage:
    poetry run python src/visualize_census.py data/short_cusp_12
    poetry run python src/visualize_census.py data/short_cusp_12 -o my_report.pdf
"""

import argparse
import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def load_census_data(census_path: Path) -> dict:
    """Load the combined data.json from a census directory.

    Args:
        census_path: Path to the census root directory.

    Returns:
        Dict mapping environment names to their gathered data.
    """
    data_path = census_path / "data.json"
    with open(data_path, "r") as f:
        return json.load(f)


def extract_max_embeddings(census_data: dict) -> list[int]:
    """Extract max_embeddings values from all environments that have info.

    Args:
        census_data: Combined census data from data.json.

    Returns:
        List of max_embeddings values.
    """
    values = []
    for env_data in census_data.values():
        info = env_data.get("info")
        if info is None:
            continue
        max_emb = info.get("max_embeddings")
        if max_emb is not None:
            values.append(max_emb)
    return values


def plot_max_embeddings_histogram(ax: plt.Axes, census_data: dict) -> None:
    """Plot a histogram of info.max_embeddings across environments.

    Args:
        ax: Matplotlib axes to draw on.
        census_data: Combined census data from data.json.
    """
    values = extract_max_embeddings(census_data)
    if not values:
        ax.text(
            0.5, 0.5, "No max_embeddings data available",
            ha="center", va="center", transform=ax.transAxes,
        )
        return

    lo, hi = min(values), max(values)
    # Integer-aligned bins: one bin per unit, with edges at half-integers
    bins = range(lo, hi + 2)
    ax.hist(values, bins=bins, edgecolor="black", alpha=0.7, align="left")
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.set_xlabel("Max Embeddings")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Max Embeddings Across Environments")


def extract_runtimes(census_data: dict) -> list[float]:
    """Extract runtime values from all environments that have info.

    Args:
        census_data: Combined census data from data.json.

    Returns:
        List of runtime values in seconds.
    """
    values = []
    for env_data in census_data.values():
        info = env_data.get("info")
        if info is None:
            continue
        runtime = info.get("runtime")
        if runtime is not None:
            values.append(runtime)
    return values


def plot_runtime_histogram(ax: plt.Axes, census_data: dict) -> None:
    """Plot a histogram of info.runtime across environments.

    Args:
        ax: Matplotlib axes to draw on.
        census_data: Combined census data from data.json.
    """
    values = extract_runtimes(census_data)
    if not values:
        ax.text(
            0.5, 0.5, "No runtime data available",
            ha="center", va="center", transform=ax.transAxes,
        )
        return

    ax.hist(values, bins="auto", edgecolor="black", alpha=0.7)
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.set_xlabel("Runtime (seconds)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Solver Runtime Across Environments")


def extract_iterations(census_data: dict) -> list[int]:
    """Extract iterations values from all environments that have info.

    Args:
        census_data: Combined census data from data.json.

    Returns:
        List of iteration counts.
    """
    values = []
    for env_data in census_data.values():
        info = env_data.get("info")
        if info is None:
            continue
        iterations = info.get("iterations")
        if iterations is not None:
            values.append(iterations)
    return values


def plot_iterations_histogram(ax: plt.Axes, census_data: dict) -> None:
    """Plot a histogram of info.iterations across environments.

    Args:
        ax: Matplotlib axes to draw on.
        census_data: Combined census data from data.json.
    """
    values = extract_iterations(census_data)
    if not values:
        ax.text(
            0.5, 0.5, "No iterations data available",
            ha="center", va="center", transform=ax.transAxes,
        )
        return

    ax.hist(values, bins="auto", edgecolor="black", alpha=0.7)
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Solver Iterations Across Environments")


def extract_info_pairs(
    census_data: dict, key_x: str, key_y: str
) -> tuple[list, list]:
    """Extract paired values from info for environments that have both keys.

    Args:
        census_data: Combined census data from data.json.
        key_x: Info field name for the x values.
        key_y: Info field name for the y values.

    Returns:
        Tuple of (x_values, y_values) lists.
    """
    xs, ys = [], []
    for env_data in census_data.values():
        info = env_data.get("info")
        if info is None:
            continue
        x = info.get(key_x)
        y = info.get(key_y)
        if x is not None and y is not None:
            xs.append(x)
            ys.append(y)
    return xs, ys


def plot_max_embeddings_vs_runtime(ax: plt.Axes, census_data: dict) -> None:
    """Scatter plot of max_embeddings vs runtime.

    Args:
        ax: Matplotlib axes to draw on.
        census_data: Combined census data from data.json.
    """
    max_embs, runtimes = extract_info_pairs(census_data, "max_embeddings", "runtime")
    if not max_embs:
        ax.text(
            0.5, 0.5, "No data available",
            ha="center", va="center", transform=ax.transAxes,
        )
        return

    ax.scatter(max_embs, runtimes, alpha=0.7, edgecolors="black", linewidths=0.5)
    ax.set_xlabel("Max Embeddings")
    ax.set_ylabel("Runtime (seconds)")
    ax.set_title("Max Embeddings vs Runtime")


def generate_pdf(census_data: dict, output_path: Path) -> None:
    """Generate a multi-page PDF of census visualizations.

    Args:
        census_data: Combined census data from data.json.
        output_path: Path for the output PDF file.
    """
    with PdfPages(output_path) as pdf:
        fig, ax = plt.subplots(figsize=(8, 5))
        plot_max_embeddings_histogram(ax, census_data)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 5))
        plot_runtime_histogram(ax, census_data)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 5))
        plot_iterations_histogram(ax, census_data)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 5))
        plot_max_embeddings_vs_runtime(ax, census_data)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="MP-VIZ|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Visualize census data from a gathered data.json"
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
        help="Output PDF path (default: <census_dir>/census_report.pdf)",
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

    output_path = Path(args.output) if args.output else census_path / "census_report.pdf"
    generate_pdf(census_data, output_path)
    logging.info(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
