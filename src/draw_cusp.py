"""Draw a cusp cellulation from a solve environment using exact cyclotomic geometry.

Loads the cusp tiling and any saved embeddings from a search environment
directory, rebuilds the cusp geometry via the appropriate cusp constructor
(using the ``pattern`` and ``pattern_type`` fields of ``config.json``), and
renders each state as a PNG/SVG using the 12-cyclotomic corner positions
from ``CuspGeometry``. With ``--format tex`` the same geometry is emitted
as a TikZ snippet suitable for ``\\input``-ing into a LaTeX document.

Three sources of embedding state can be drawn:

    - ``completions``: each completed embedding in ``out.jsonl``
    - ``max``: the peak-embedding state captured in ``max_embeddings_state.json``
    - ``checkpoint``: the current placed embeddings reconstructed from
      ``checkpoint.json`` (mirrors ``Solver.load_checkpoint``)

The same data can also come from a census ``data.json`` produced by
``gather_census.py``, which bundles all of the above per environment.

Supported pattern types: ``"finger"`` and ``"long_cusp"``.

Usage:
    poetry run python src/draw_cusp.py <env_dir>
    poetry run python src/draw_cusp.py <env_dir> --state max
    poetry run python src/draw_cusp.py --data-json <data.json> --env <name>
    poetry run python src/draw_cusp.py --data-json <data.json> -o <out_dir>
"""

import argparse
import json
import logging
from pathlib import Path

import cairo

from base import (
    CUSP_CELL_TYPE_SHORT_LABEL,
    CuspCell,
    MANIFOLD_CELL_TYPE_SHORT_LABEL,
)
from construction import Construction, Cusp, Embeddings, load_traversal
from cusp_geometry import CuspGeometry
from draw import (
    generate_spread_color_map,
    get_centroid,
    nudge_to_centroid,
    show_centered_text,
)
from env import read_checkpoint, read_config
from finger_cusp import FingerCuspConstructor, parse_finger_pattern
from long_cusp import LongCuspConstructor


def cell_verts(
    geo: CuspGeometry, cusp_cell: CuspCell
) -> list[tuple[float, float]]:
    """Returns the (x, y) corner coordinates of a cell in corner-index order.

    Args:
        geo: The cusp geometry holding cyclotomic corner positions.
        cusp_cell: The triangle or square whose corners are being looked up.

    Returns:
        List of ``(x, y)`` floats, one per corner, indexed from corner 1
        upward. A triangle yields 3 points; a square yields 4.

    Raises:
        ValueError: If any corner of ``cusp_cell`` is unassigned in ``geo``.
    """
    n = 3 if cusp_cell.is_tri() else 4
    verts: list[tuple[float, float]] = []
    for corner in range(1, n + 1):
        pos = geo.get_corner(cusp_cell, corner)
        if pos is None:
            raise ValueError(f"{cusp_cell!r} corner {corner} has no position")
        z = pos.to_complex()
        verts.append((z.real, z.imag))
    return verts


def compute_bounds(
    geo: CuspGeometry,
) -> tuple[float, float, float, float]:
    """Returns ``(xmin, ymin, xmax, ymax)`` for all positions in ``geo``."""
    xs: list[float] = []
    ys: list[float] = []
    for _, _, pos in geo:
        z = pos.to_complex()
        xs.append(z.real)
        ys.append(z.imag)
    if not xs:
        raise ValueError("cusp geometry is empty")
    return min(xs), min(ys), max(xs), max(ys)


def draw_empty_cell(ctx: cairo.Context, verts: list[tuple[float, float]]) -> None:
    """Stroke a cell outline with no fill and no labels."""
    ctx.save()
    ctx.move_to(*verts[0])
    for p in verts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    ctx.set_source_rgb(0, 0, 0)
    ctx.stroke()
    ctx.restore()


def _blend_white(rgb: tuple[float, float, float], factor: float) -> tuple[float, float, float]:
    """Blend an ``(r, g, b)`` color toward white by ``factor`` in [0, 1].

    ``factor=0`` returns the color unchanged; ``factor=1`` returns white.
    """
    r, g, b = rgb
    return (
        r + factor * (1 - r),
        g + factor * (1 - g),
        b + factor * (1 - b),
    )


def draw_embedded_cell(
    ctx: cairo.Context,
    verts: list[tuple[float, float]],
    embedding_labels,
    color_map,
    color_idx: int,
    annotation: str | None = None,
    lighten: bool = False,
    bold_edges: bool = False,
    manifold_label: str | None = None,
    cusp_label: str | None = None,
) -> None:
    """Fill a cell with a color-coded manifold cell and label its vertices.

    The cell interior shows the cusp-vertex index (``embedding_labels[0]``)
    at the centroid; each corner is labeled with the manifold-vertex index
    mapped to it by the embedding, slightly nudged inward from the corner.

    Args:
        ctx: Cairo context with the cyclotomic-to-device CTM already set up.
        verts: Corner positions in corner-index order (``corner_1, ..., corner_k``).
        embedding_labels: The embedding spec tuple ``(v0, v1, ..., vk)``
            where ``v0`` is the cusp vertex and ``v1..vk`` are the corner
            vertex indices matching ``verts``.
        color_map: Precomputed list of RGB tuples.
        color_idx: Index into ``color_map`` selecting this cell's fill color.
        annotation: Optional small tag (e.g. ``"3R*"``) rendered near the
            centroid to carry solver-state info for debug illustrations.
        lighten: When True, blend the fill color toward white so this cell
            reads as visually lighter (used to mark induced embeddings).
        bold_edges: When True, stroke the cell outline with a heavier
            line width (used to highlight the current stack frame).
        manifold_label: Optional short identifier (e.g. ``"TET[0]"``)
            rendered opposite the stack-annotation slot.
        cusp_label: Optional short identifier (e.g. ``"SQR[2]"``)
            rendered near corner 2.
    """
    ctx.save()

    ctx.move_to(*verts[0])
    for p in verts[1:]:
        ctx.line_to(*p)
    ctx.close_path()

    r, g, b = color_map[color_idx]
    if lighten:
        r, g, b = _blend_white((r, g, b), 0.5)
    ctx.set_source_rgb(r, g, b)
    ctx.fill_preserve()
    ctx.set_source_rgb(0, 0, 0)
    if bold_edges:
        saved_line_width = ctx.get_line_width()
        ctx.set_line_width(saved_line_width * 3.0)
        ctx.stroke()
        ctx.set_line_width(saved_line_width)
    else:
        ctx.stroke()

    ctx.set_source_rgb(0, 0, 0)
    centroid = get_centroid(verts)
    show_centered_text(ctx, centroid[0], centroid[1], str(embedding_labels[0]))

    for i, p in enumerate(verts):
        p_ = nudge_to_centroid(p, centroid, 0.35)
        show_centered_text(ctx, p_[0], p_[1], str(embedding_labels[i + 1]))

    if annotation or manifold_label or cusp_label:
        # Smaller font for the tag/manifold label; the stack tag sits
        # between corner 1's label and the centroid, the manifold label
        # sits on the opposite side near the last corner.
        small_font_size = 0.10
        saved_matrix = ctx.get_font_matrix()
        ctx.set_font_matrix(
            cairo.Matrix(
                xx=small_font_size, yx=0, xy=0, yy=-small_font_size, x0=0, y0=0
            )
        )
        if annotation:
            ctx.select_font_face(
                "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
            )
            tag_pos = nudge_to_centroid(verts[0], centroid, 0.65)
            show_centered_text(ctx, tag_pos[0], tag_pos[1], annotation)
            ctx.select_font_face(
                "Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
            )
        if manifold_label:
            ml_pos = nudge_to_centroid(verts[-1], centroid, 0.65)
            show_centered_text(ctx, ml_pos[0], ml_pos[1], manifold_label)
        if cusp_label:
            cl_pos = nudge_to_centroid(verts[1], centroid, 0.65)
            show_centered_text(ctx, cl_pos[0], cl_pos[1], cusp_label)
        ctx.set_font_matrix(saved_matrix)

    ctx.restore()


def _make_surface(output_filename: str, width: int, height: int):
    """Create a cairo surface for the requested output format."""
    if output_filename.endswith(".svg"):
        return cairo.SVGSurface(output_filename, width, height)
    if output_filename.endswith(".png"):
        return cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    raise ValueError("Unsupported file format. Use .svg or .png")


def draw_cusp(
    geo: CuspGeometry,
    construction: Construction,
    output_filename: str,
    width: int = 2048,
    height: int = 1024,
    margin: int = 50,
    annotations: dict[CuspCell, str] | None = None,
    induced_cells: set[CuspCell] | None = None,
    bold_edge_cells: set[CuspCell] | None = None,
    width_cm: float = 14.0,
) -> None:
    """Render the cusp cellulation to ``output_filename``.

    Dispatches on the output file extension: ``.png`` and ``.svg`` go
    through the cairo renderer; ``.tex`` emits a TikZ snippet.

    Args:
        geo: Exact cyclotomic geometry of the cusp tiling.
        construction: Carries the cusp (pairings), current embeddings,
            and the manifold-cell counts used to pick colors.
        output_filename: Target file (``.png``, ``.svg``, or ``.tex``).
        width: (cairo only) Output canvas width in device pixels.
        height: (cairo only) Output canvas height in device pixels.
        margin: (cairo only) Padding in device pixels between content
            bbox and canvas.
        annotations: Optional ``{cusp_cell: tag}`` map; matched embedded
            cells render the tag near their centroid (debug feature).
        induced_cells: Optional set of cusp cells whose fill should be
            lightened to distinguish induced embeddings from iterator
            candidates (debug feature).
        bold_edge_cells: Optional set of cusp cells whose outlines should
            be stroked heavier, used to highlight the current stack
            frame (debug feature).
        width_cm: (tikz only) Target width of the figure in centimeters;
            the picture is scaled uniformly so the geometry bbox fits
            this width.
    """
    if output_filename.endswith(".tex"):
        _draw_cusp_tikz(
            geo,
            construction,
            output_filename,
            annotations=annotations,
            induced_cells=induced_cells,
            bold_edge_cells=bold_edge_cells,
            width_cm=width_cm,
        )
        return

    _draw_cusp_cairo(
        geo,
        construction,
        output_filename,
        width=width,
        height=height,
        margin=margin,
        annotations=annotations,
        induced_cells=induced_cells,
        bold_edge_cells=bold_edge_cells,
    )


def _draw_cusp_cairo(
    geo: CuspGeometry,
    construction: Construction,
    output_filename: str,
    width: int,
    height: int,
    margin: int,
    annotations: dict[CuspCell, str] | None,
    induced_cells: set[CuspCell] | None,
    bold_edge_cells: set[CuspCell] | None,
) -> None:
    """Render the cusp cellulation to a ``.png`` or ``.svg`` using cairo."""
    surface = _make_surface(output_filename, width, height)
    ctx = cairo.Context(surface)

    # White background (image surfaces default to transparent).
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # Fit the geometry bbox into the canvas interior with a uniform scale.
    xmin, ymin, xmax, ymax = compute_bounds(geo)
    w = max(xmax - xmin, 1e-9)
    h = max(ymax - ymin, 1e-9)
    scale = min((width - 2 * margin) / w, (height - 2 * margin) / h)

    # Center the (possibly narrower-than-canvas) content in the margin box.
    tx = margin + (width - 2 * margin - scale * w) / 2
    ty = height - margin - (height - 2 * margin - scale * h) / 2

    ctx.translate(tx, ty)
    ctx.scale(scale, -scale)
    ctx.translate(-xmin, -ymin)

    # A 2-device-pixel stroke after the scale is applied.
    ctx.set_line_width(4.0 / scale)

    # Font matrix: y-flipped to counteract the ctx.scale(_, -scale) above.
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    font_size = 0.162
    ctx.set_font_matrix(
        cairo.Matrix(xx=font_size, yx=0, xy=0, yy=-font_size, x0=0, y0=0)
    )

    color_map = generate_spread_color_map(
        construction.num_tets + construction.num_octs, s=0.8, v=0.9
    )

    for cusp_cell in geo.cells():
        if not geo.is_cell_complete(cusp_cell):
            continue
        verts = cell_verts(geo, cusp_cell)
        embedding = construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)
        if embedding is None:
            draw_empty_cell(ctx, verts)
            continue
        if embedding.manifold_cell.is_tet():
            color_idx = embedding.manifold_cell.cell_index
        else:
            color_idx = construction.num_tets + embedding.manifold_cell.cell_index
        annotation = annotations.get(cusp_cell) if annotations else None
        lighten = bool(induced_cells and cusp_cell in induced_cells)
        bold_edges = bool(bold_edge_cells and cusp_cell in bold_edge_cells)
        m = embedding.manifold_cell
        manifold_label = (
            f"{MANIFOLD_CELL_TYPE_SHORT_LABEL[m.cell_type].upper()}"
            f"[{m.cell_index}]"
        )
        cusp_label = (
            f"{CUSP_CELL_TYPE_SHORT_LABEL[cusp_cell.cell_type].upper()}"
            f"[{cusp_cell.cell_index}]"
        )
        draw_embedded_cell(
            ctx,
            verts,
            embedding.embedding_spec,
            color_map,
            color_idx,
            annotation=annotation,
            lighten=lighten,
            bold_edges=bold_edges,
            manifold_label=manifold_label,
            cusp_label=cusp_label,
        )

    if output_filename.endswith(".png"):
        surface.write_to_png(output_filename)
    else:
        surface.finish()


def _tikz_coord(p: tuple[float, float], xmin: float, ymin: float) -> str:
    """Format an ``(x, y)`` point for TikZ, shifted so (xmin, ymin) → origin."""
    return f"({p[0] - xmin:.4f},{p[1] - ymin:.4f})"


def _tikz_rgb(rgb: tuple[float, float, float]) -> str:
    """Format an RGB triple as an xcolor inline expression."""
    r, g, b = rgb
    return f"{{rgb,1:red,{r:.4f};green,{g:.4f};blue,{b:.4f}}}"


def _draw_cusp_tikz(
    geo: CuspGeometry,
    construction: Construction,
    output_filename: str,
    annotations: dict[CuspCell, str] | None,
    induced_cells: set[CuspCell] | None,
    bold_edge_cells: set[CuspCell] | None,
    width_cm: float,
) -> None:
    """Render the cusp cellulation to a TikZ snippet at ``output_filename``.

    The emitted file contains a single ``tikzpicture`` environment with
    inline xcolor RGB expressions so snippets can be concatenated without
    color-name collisions. Requires ``\\usepackage{tikz}`` and
    ``\\usepackage{xcolor}`` in the consuming document's preamble.
    """
    xmin, ymin, xmax, ymax = compute_bounds(geo)
    w_geo = max(xmax - xmin, 1e-9)
    h_geo = max(ymax - ymin, 1e-9)
    scale_cm = width_cm / w_geo

    color_map = generate_spread_color_map(
        construction.num_tets + construction.num_octs, s=0.8, v=0.9
    )

    normal_lw_pt = 0.4
    bold_lw_pt = 1.2

    lines: list[str] = []
    lines.append(
        "% TikZ snippet produced by mixed-platonic/draw_cusp.py"
    )
    lines.append(
        "% Requires: \\usepackage{tikz} and \\usepackage{xcolor}"
    )
    lines.append(
        f"\\begin{{tikzpicture}}[x={scale_cm:.4f}cm,y={scale_cm:.4f}cm]"
    )

    for cusp_cell in geo.cells():
        if not geo.is_cell_complete(cusp_cell):
            continue
        verts = cell_verts(geo, cusp_cell)
        path = (
            " -- ".join(_tikz_coord(v, xmin, ymin) for v in verts) + " -- cycle"
        )
        embedding = construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)

        if embedding is None:
            lines.append(
                f"  \\draw[line width={normal_lw_pt}pt] {path};"
            )
            continue

        if embedding.manifold_cell.is_tet():
            color_idx = embedding.manifold_cell.cell_index
        else:
            color_idx = construction.num_tets + embedding.manifold_cell.cell_index
        lighten = bool(induced_cells and cusp_cell in induced_cells)
        bold_edges = bool(bold_edge_cells and cusp_cell in bold_edge_cells)

        r, g, b = color_map[color_idx]
        if lighten:
            r, g, b = _blend_white((r, g, b), 0.5)
        fill_expr = _tikz_rgb((r, g, b))
        lw_pt = bold_lw_pt if bold_edges else normal_lw_pt
        lines.append(
            f"  \\filldraw[fill={fill_expr}, draw=black, "
            f"line width={lw_pt}pt] {path};"
        )

        spec = embedding.embedding_spec
        centroid = get_centroid(verts)

        # Centroid label: cusp vertex index.
        lines.append(
            f"  \\node[font=\\footnotesize] at "
            f"{_tikz_coord(centroid, xmin, ymin)} {{{spec[0]}}};"
        )

        # Corner labels: manifold vertex per corner.
        for i, p in enumerate(verts):
            p_ = nudge_to_centroid(p, centroid, 0.35)
            lines.append(
                f"  \\node[font=\\footnotesize] at "
                f"{_tikz_coord(p_, xmin, ymin)} {{{spec[i + 1]}}};"
            )

        # Small-font tags matching the cairo layout.
        m = embedding.manifold_cell
        manifold_label = (
            f"{MANIFOLD_CELL_TYPE_SHORT_LABEL[m.cell_type].upper()}"
            f"[{m.cell_index}]"
        )
        cusp_label = (
            f"{CUSP_CELL_TYPE_SHORT_LABEL[cusp_cell.cell_type].upper()}"
            f"[{cusp_cell.cell_index}]"
        )
        annotation = annotations.get(cusp_cell) if annotations else None

        if annotation:
            tag_pos = nudge_to_centroid(verts[0], centroid, 0.65)
            lines.append(
                f"  \\node[font=\\scriptsize\\bfseries] at "
                f"{_tikz_coord(tag_pos, xmin, ymin)} {{{annotation}}};"
            )
        ml_pos = nudge_to_centroid(verts[-1], centroid, 0.65)
        lines.append(
            f"  \\node[font=\\scriptsize] at "
            f"{_tikz_coord(ml_pos, xmin, ymin)} {{{manifold_label}}};"
        )
        cl_pos = nudge_to_centroid(verts[1], centroid, 0.65)
        lines.append(
            f"  \\node[font=\\scriptsize] at "
            f"{_tikz_coord(cl_pos, xmin, ymin)} {{{cusp_label}}};"
        )

    lines.append("\\end{tikzpicture}")

    Path(output_filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_finger_cusp_geometry(finger_pattern) -> CuspGeometry:
    """Build the cyclotomic geometry for a finger-pattern cusp.

    Args:
        finger_pattern: 0/1 integer list encoding the orientation string.

    Returns:
        A ``CuspGeometry`` whose corners are populated per the
        ``FingerCuspConstructor.cusp_geometry`` convention.
    """
    constructor = FingerCuspConstructor(Cusp(), finger_pattern)
    return constructor.cusp_geometry()


def build_long_cusp_geometry(long_cusp_pattern: str) -> CuspGeometry:
    """Build the cyclotomic geometry for a long-cusp pattern.

    Args:
        long_cusp_pattern: Cyclic strip-label sequence over ``{a, b, c, d, e}``.

    Returns:
        A ``CuspGeometry`` populated per ``LongCuspConstructor.cusp_geometry``.
    """
    constructor = LongCuspConstructor(Cusp(), long_cusp_pattern)
    return constructor.cusp_geometry()


def load_construction_from_config(config: dict) -> Construction:
    """Reconstruct a ``Construction`` (cusp + traversal + cell counts) from config.

    Embeddings are left empty; callers populate them per completion.

    Args:
        config: Config dict as returned by ``read_config``.
    """
    cusp = Cusp()
    cusp.load(config["cusp"])
    traversal = load_traversal(config["traversal"])
    embeddings = Embeddings()
    return Construction(
        cusp, embeddings, traversal, config["num_tets"], config["num_octs"]
    )


def iter_completed_embeddings(env_path: Path):
    """Yield the serialized embedding lists from ``out.jsonl``, if any."""
    out_path = env_path / "out.jsonl"
    if not out_path.exists():
        return
    with open(out_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)["embeddings"]


def load_max_embeddings_dump(env_path: Path) -> list | None:
    """Load ``max_embeddings_state.json`` as an embeddings dump, or None."""
    path = env_path / "max_embeddings_state.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def checkpoint_dict_to_dump(checkpoint: dict) -> list:
    """Flatten a checkpoint dict's placed embeddings into a single dump list.

    Mirrors the semantics of ``Solver.load_checkpoint``: every frame except
    the topmost has its ``embedding`` and ``induced_embeddings`` currently
    placed in the ``Embeddings`` collection. The topmost frame's embedding
    is the next candidate to try and is not yet placed.

    Args:
        checkpoint: Checkpoint dict as produced by ``Solver.save_checkpoint``.

    Returns:
        A list of embedding tuples compatible with ``Embeddings.load``.
    """
    frames = checkpoint.get("stack", [])
    dump: list = []
    for i, frame_data in enumerate(frames):
        if i >= len(frames) - 1:
            break
        if frame_data["embedding"] is not None:
            dump.append(frame_data["embedding"])
        dump.extend(frame_data["induced_embeddings"])
    return dump


def load_checkpoint_embeddings_dump(env_path: Path) -> list | None:
    """Reconstruct the placed embeddings from ``checkpoint.json``, or None."""
    checkpoint = read_checkpoint(env_path)
    if checkpoint is None:
        return None
    return checkpoint_dict_to_dump(checkpoint)


def load_env_data_from_dir(env_path: Path) -> dict:
    """Gather the four draw inputs for an env directory.

    Returns a dict with keys:
        config: config.json contents
        completions: list of embedding dumps (possibly empty)
        max: max_embeddings_state dump, or None
        checkpoint_dump: flattened checkpoint embeddings, or None
    """
    return {
        "config": read_config(env_path),
        "completions": list(iter_completed_embeddings(env_path)),
        "max": load_max_embeddings_dump(env_path),
        "checkpoint_dump": load_checkpoint_embeddings_dump(env_path),
    }


def load_env_data_from_gathered(gathered_env: dict) -> dict:
    """Gather the four draw inputs from a per-env dict inside ``data.json``.

    ``gather_census.py`` stores each env's JSON files under keys named
    after the file stems, and its JSONL files as lists. This adapter
    maps that layout back to the same shape as
    ``load_env_data_from_dir``.

    Args:
        gathered_env: Per-env dict from a gathered ``data.json``, with
            keys like ``"config"``, ``"out"``, ``"max_embeddings_state"``,
            ``"checkpoint"``.
    """
    out_entries = gathered_env.get("out") or []
    completions = [entry["embeddings"] for entry in out_entries]
    checkpoint = gathered_env.get("checkpoint")
    checkpoint_dump = (
        checkpoint_dict_to_dump(checkpoint) if checkpoint is not None else None
    )
    return {
        "config": gathered_env["config"],
        "completions": completions,
        "max": gathered_env.get("max_embeddings_state"),
        "checkpoint_dump": checkpoint_dump,
    }


def build_geometry_for_config(config: dict) -> CuspGeometry:
    """Dispatch on ``pattern_type`` to construct the cusp geometry.

    Args:
        config: Config dict as returned by ``read_config``.

    Raises:
        NotImplementedError: If ``pattern_type`` is not supported.
        ValueError: If ``pattern`` is missing.
    """
    pattern_type = config.get("pattern_type")
    pattern = config.get("pattern")
    if not pattern:
        raise ValueError(
            "config is missing 'pattern'; regenerate the environment "
            "to record the source pattern"
        )
    if pattern_type == "finger":
        return build_finger_cusp_geometry(parse_finger_pattern(pattern))
    if pattern_type == "long_cusp":
        return build_long_cusp_geometry(pattern)
    raise NotImplementedError(
        f"draw_cusp does not support pattern_type={pattern_type!r}"
    )


STATE_CHOICES = ("completions", "max", "checkpoint", "all")

FORMAT_CHOICES = ("png", "svg", "tex")


def _render_dump(
    geo: CuspGeometry,
    construction: Construction,
    embeddings_dump: list | None,
    filename: str,
) -> None:
    """Load an embeddings dump into ``construction`` and render to ``filename``."""
    construction.embeddings = Embeddings()
    if embeddings_dump is not None:
        construction.embeddings.load(embeddings_dump)
    draw_cusp(geo, construction, filename)


def draw_env_data(
    env_data: dict,
    output_prefix: str,
    state: str = "all",
    fmt: str = "png",
) -> list[str]:
    """Render cusp images from a unified env-data dict.

    ``env_data`` has the shape produced by ``load_env_data_from_dir`` or
    ``load_env_data_from_gathered``: ``config``, ``completions`` (list),
    ``max`` (dump or None), ``checkpoint_dump`` (dump or None).

    Writes images depending on ``state``:

    - ``"completions"``: one image per completion.
    - ``"max"``: one image for the max-embeddings dump.
    - ``"checkpoint"``: one image for the checkpoint's placed embeddings.
    - ``"all"``: every state above that is present.

    If none of the selected states are present, writes a single empty-cusp
    image to ``<prefix>.<fmt>``.

    Args:
        env_data: Gathered per-env draw inputs.
        output_prefix: Path prefix for output files; per-state suffixes
            (``_<i>``, ``_max``, ``_checkpoint``) are appended automatically.
        state: Which states to draw; one of ``STATE_CHOICES``.
        fmt: Output format; one of ``FORMAT_CHOICES``. ``"tex"`` produces
            TikZ snippets, the others produce raster/vector images.

    Returns:
        List of output file paths written.
    """
    if state not in STATE_CHOICES:
        raise ValueError(
            f"unknown state {state!r}; expected one of {STATE_CHOICES}"
        )
    if fmt not in FORMAT_CHOICES:
        raise ValueError(
            f"unknown fmt {fmt!r}; expected one of {FORMAT_CHOICES}"
        )

    geo = build_geometry_for_config(env_data["config"])
    construction = load_construction_from_config(env_data["config"])

    written: list[str] = []
    if state in ("completions", "all"):
        for i, dump in enumerate(env_data["completions"]):
            filename = f"{output_prefix}_{i}.{fmt}"
            _render_dump(geo, construction, dump, filename)
            written.append(filename)
    if state in ("max", "all") and env_data["max"] is not None:
        filename = f"{output_prefix}_max.{fmt}"
        _render_dump(geo, construction, env_data["max"], filename)
        written.append(filename)
    if state in ("checkpoint", "all") and env_data["checkpoint_dump"] is not None:
        filename = f"{output_prefix}_checkpoint.{fmt}"
        _render_dump(geo, construction, env_data["checkpoint_dump"], filename)
        written.append(filename)

    if not written:
        filename = f"{output_prefix}.{fmt}"
        _render_dump(geo, construction, None, filename)
        written.append(filename)

    return written


def draw_env(
    env_path: Path,
    output_prefix: str | None = None,
    state: str = "all",
    fmt: str = "png",
) -> list[str]:
    """Render cusp images for a search environment directory.

    Thin wrapper around ``draw_env_data`` that reads the env's files.

    Args:
        env_path: Path to the search environment directory.
        output_prefix: Path prefix for output files. Defaults to
            ``<env_path>/cusp``.
        state: Which states to draw; one of ``STATE_CHOICES``.
        fmt: Output format; one of ``FORMAT_CHOICES``.
    """
    if output_prefix is None:
        output_prefix = str(env_path / "cusp")
    env_data = load_env_data_from_dir(env_path)
    return draw_env_data(env_data, output_prefix, state=state, fmt=fmt)


def draw_from_data_json(
    data_path: Path,
    output_dir: Path,
    env_name: str | None = None,
    state: str = "all",
    fmt: str = "png",
) -> list[str]:
    """Render cusp images from a census ``data.json`` produced by ``gather_census``.

    Writes output files into ``output_dir`` with per-env prefix
    ``<env_name>`` (e.g. ``<output_dir>/++--++--++--_max.png``).
    ``output_dir`` is created if it does not exist.

    Args:
        data_path: Path to a gathered ``data.json``.
        output_dir: Directory to write images into.
        env_name: Single env name to draw. If ``None``, iterates all envs
            in the data file.
        state: Which states to draw; one of ``STATE_CHOICES``.
        fmt: Output format; one of ``FORMAT_CHOICES``.

    Returns:
        List of output file paths written (across all envs).
    """
    with open(data_path, "r") as f:
        gathered = json.load(f)

    if env_name is not None:
        if env_name not in gathered:
            raise KeyError(
                f"env {env_name!r} not present in {data_path}; "
                f"available: {sorted(gathered.keys())[:5]}..."
            )
        env_names = [env_name]
    else:
        env_names = sorted(gathered.keys())

    output_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for name in env_names:
        env_data = load_env_data_from_gathered(gathered[name])
        prefix = str(output_dir / name)
        written.extend(draw_env_data(env_data, prefix, state=state, fmt=fmt))
    return written


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="MP-DRAW-CUSP|%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Draw the cusp cellulation of a solve environment"
    )
    parser.add_argument(
        "env",
        type=str,
        nargs="?",
        help="Path to a search environment directory (omit with --data-json)",
    )
    parser.add_argument(
        "--data-json",
        type=str,
        default=None,
        help="Path to a gathered census data.json; overrides positional env "
        "and reads all envs (or a single --env) from the bundle",
    )
    parser.add_argument(
        "--env",
        dest="env_name",
        type=str,
        default=None,
        help="With --data-json, restrict to this env name (default: all envs)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Dir mode: file prefix (default: <env>/cusp). "
        "With --data-json: output directory (default: <data.json dir>/draw)",
    )
    parser.add_argument(
        "--state",
        choices=STATE_CHOICES,
        default="all",
        help="Which saved state(s) to render (default: all)",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=FORMAT_CHOICES,
        default="png",
        help=(
            "Output format: png/svg (raster/vector images) or tex "
            "(TikZ snippets). Default: png."
        ),
    )

    args = parser.parse_args()

    if args.data_json is not None:
        data_path = Path(args.data_json)
        if not data_path.is_file():
            parser.error(f"data.json does not exist: {data_path}")
        output_dir = (
            Path(args.output) if args.output else data_path.parent / "draw"
        )
        written = draw_from_data_json(
            data_path,
            output_dir,
            env_name=args.env_name,
            state=args.state,
            fmt=args.fmt,
        )
    else:
        if args.env is None:
            parser.error("either <env> or --data-json is required")
        if args.env_name is not None:
            parser.error("--env is only valid with --data-json")
        env_path = Path(args.env)
        if not env_path.is_dir():
            parser.error(f"environment directory does not exist: {env_path}")
        written = draw_env(env_path, args.output, state=args.state, fmt=args.fmt)

    for path in written:
        logging.info(f"Wrote {path}")


if __name__ == "__main__":
    main()
