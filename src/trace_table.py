"""Render a solver trace as a LaTeX table.

Reads ``trace.jsonl`` produced by ``solve.py --debug-trace`` and emits
a LaTeX ``tabular`` (or ``longtable``) whose rows are solver iterations
and whose columns are the entries on the solver's stack at the end of
each iteration, followed by a column for the consistency violation (if
any) recorded during that iteration.

Each stack cell is shown as ``cusp_cell -> manifold_cell/spec`` with a
trailing ``(+n)`` indicating the number of embeddings induced by
constraint propagation at that frame.

Usage:
    poetry run python src/trace_table.py <env_dir>
    poetry run python src/trace_table.py <env_dir> -o trace.tex
    poetry run python src/trace_table.py <env_dir> --longtable
    poetry run python src/trace_table.py <env_dir> --max-iters 200
"""

import argparse
import json
from pathlib import Path

from base import (
    CUSP_CELL_TYPE_SHORT_LABEL,
    MANIFOLD_CELL_TYPE_SHORT_LABEL,
)


def load_trace(trace_path: Path) -> list[dict]:
    """Load every record from ``trace.jsonl`` into a list of dicts."""
    records: list[dict] = []
    with open(trace_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def format_cusp_cell(cell_tuple) -> str:
    """Format a ``(cell_type, cell_index)`` tuple as ``tri[ 0]`` / ``sqr[ 0]``."""
    cell_type, cell_index = cell_tuple
    return f"{CUSP_CELL_TYPE_SHORT_LABEL[cell_type]}[{cell_index:2d}]"


def format_manifold_cell(cell_tuple) -> str:
    """Format a ``(cell_type, cell_index)`` tuple as ``tet[ 1]`` / ``oct[ 3]``."""
    cell_type, cell_index = cell_tuple
    return f"{MANIFOLD_CELL_TYPE_SHORT_LABEL[cell_type]}[{cell_index:2d}]"


def format_embedding(emb_tuple) -> str:
    """Format an embedding tuple as ``tet[ 1]/0123``."""
    _, m_cell, _c_cell, spec = emb_tuple
    spec_str = "".join(str(i) for i in spec)
    return f"{format_manifold_cell(m_cell)}/{spec_str}"


def format_frame(frame: dict) -> str:
    """Format a stack frame as a single LaTeX-ready cell string."""
    cc = format_cusp_cell(frame["cusp_cell"])
    emb = frame["embedding"]
    body = format_embedding(emb) if emb is not None else r"\emph{pending}"
    n_induced = len(frame.get("induced_embeddings") or [])
    tail = f" (+{n_induced})" if n_induced else ""
    return rf"\texttt{{{cc}->{body}}}{tail}"


def escape_violation(violation) -> str:
    """LaTeX-escape a violation string, or return an empty cell for None."""
    if not violation:
        return ""
    escaped = violation.replace("\\", r"\textbackslash{}")
    for ch in ("&", "%", "$", "#", "_", "{", "}"):
        escaped = escaped.replace(ch, f"\\{ch}")
    return escaped


def render_table(traces: list[dict], use_longtable: bool = False) -> str:
    """Build the LaTeX table source from a list of trace records."""
    if not traces:
        env = "longtable" if use_longtable else "tabular"
        return f"\\begin{{{env}}}{{l}}\n% empty trace\n\\end{{{env}}}\n"

    max_depth = max(len(t["stack"]) for t in traces)
    col_spec = "r" + "l" * max_depth + "l"

    header_cells = (
        ["Iter"]
        + [f"Depth {i + 1}" for i in range(max_depth)]
        + ["Violation"]
    )
    header_row = " & ".join(header_cells) + r" \\"

    data_rows: list[str] = []
    for t in traces:
        cells = [str(t["counter"])]
        stack = t["stack"]
        for i in range(max_depth):
            cells.append(format_frame(stack[i]) if i < len(stack) else "")
        cells.append(escape_violation(t.get("violation")))
        data_rows.append(" & ".join(cells) + r" \\")

    if use_longtable:
        return (
            f"\\begin{{longtable}}{{{col_spec}}}\n"
            f"\\toprule\n"
            f"{header_row}\n"
            f"\\midrule\n"
            f"\\endfirsthead\n"
            f"\\toprule\n"
            f"{header_row}\n"
            f"\\midrule\n"
            f"\\endhead\n"
            f"\\bottomrule\n"
            f"\\endfoot\n"
            + "\n".join(data_rows) + "\n"
            f"\\end{{longtable}}\n"
        )

    return (
        f"\\begin{{tabular}}{{{col_spec}}}\n"
        f"\\toprule\n"
        f"{header_row}\n"
        f"\\midrule\n"
        + "\n".join(data_rows) + "\n"
        f"\\bottomrule\n"
        f"\\end{{tabular}}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a solver trace.jsonl as a LaTeX table"
    )
    parser.add_argument(
        "env",
        type=str,
        help="Path to a search environment directory containing trace.jsonl",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Write LaTeX to this file (default: stdout)",
    )
    parser.add_argument(
        "--longtable",
        action="store_true",
        help="Emit a longtable (multi-page) instead of a tabular",
    )
    parser.add_argument(
        "--max-iters",
        type=int,
        default=None,
        help="Truncate the trace to the first N iterations",
    )
    args = parser.parse_args()

    env_path = Path(args.env)
    trace_path = env_path / "trace.jsonl"
    if not trace_path.is_file():
        parser.error(f"trace file does not exist: {trace_path}")

    traces = load_trace(trace_path)
    if args.max_iters is not None:
        traces = traces[: args.max_iters]

    latex = render_table(traces, use_longtable=args.longtable)

    if args.output:
        Path(args.output).write_text(latex, encoding="utf-8")
    else:
        print(latex, end="")


if __name__ == "__main__":
    main()
