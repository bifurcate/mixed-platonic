# Mixed-Platonic

Combinatorial enumeration of cusped hyperbolic 3-manifolds decomposed into
regular ideal tetrahedra and octahedra.

## Background

A cusped hyperbolic 3-manifold can be decomposed into ideal polyhedra — polyhedra
whose vertices lie on the boundary at infinity of hyperbolic space. This project
focuses on decompositions using two types of regular ideal polyhedra:

- **Tetrahedra** (4 vertices, 4 triangular faces)
- **Octahedra** (6 vertices, 8 triangular faces)

Each ideal vertex of a polyhedron contributes a polygonal cross-section to the
cusp boundary: a tetrahedron contributes an equilateral **triangle**, and an
octahedron contributes a **square**. The cusp boundary is therefore tiled by
triangles and squares, and two cusp cells share an edge exactly when the
corresponding polyhedra share a face in the manifold.

The key insight is that this correspondence allows the 3-dimensional gluing
problem to be reduced to a 2-dimensional combinatorial search: given a cusp
tiling, find all valid ways to assign manifold cell vertices to cusp cells
such that the induced face pairings are consistent.

## Algorithm

The search is a recursive backtracking algorithm with constraint propagation:

1. **Generate** a cusp tiling from a pattern (finger or long cusp pattern).
2. **Embed** cusp cells one at a time in traversal order, trying each valid
   (manifold cell, vertex, permutation) combination.
3. **Propagate** — after each placement, neighboring cusp cells may have their
   embeddings fully determined. These induced embeddings are added automatically.
   If a contradiction arises, backtrack.
4. **Complete** — when every cusp cell has an embedding, the result is a valid
   manifold cellulation. Export it to [Regina](https://regina-normal.github.io/)
   for topological analysis.

## Installation

Requires Python 3.10+ and [Poetry](https://python-poetry.org/).

```sh
poetry install
```

**Note:** The `regina` package may require additional system-level dependencies.
See the [Regina installation guide](https://regina-normal.github.io/install/) for details.

## Usage

### 1. Generate a search environment

Create a search environment from a finger pattern:

```sh
poetry run python src/construct.py -f "+-+-+-+-+-+-" my_search
```

Or from a long cusp pattern:

```sh
poetry run python src/construct.py -l "a" my_search
```

This creates a directory (`my_search/`) containing `config.json` and `state.json`.

### 2. Run the solver

```sh
poetry run python src/solve.py my_search
```

Solutions are written to `my_search/out.jsonl`, one per line.

The solver supports **stop/resume**: pressing Ctrl+C saves a checkpoint to
the environment directory. Running the same command again detects the
checkpoint and resumes from where it left off:

```sh
# First run — press Ctrl+C to stop early
poetry run python src/solve.py my_search
# ^C — checkpoint saved

# Resume from checkpoint
poetry run python src/solve.py my_search
```

### 3. Analyze results

Extract Regina isomorphism signatures from completed solutions:

```sh
poetry run python src/analyze.py -i my_search
```

### Census workflow

A census automates the generate-construct-solve-analyze pipeline across all
distinct cusp patterns of a given size:

```sh
# 1. Generate a manifest of all finger patterns with 12 fingers
poetry run python src/generate_census.py -n 12 my_manifest.json

# 2. Construct solver environments from the manifest
#    (also copies the manifest into the census directory as manifest.json)
poetry run python src/construct_census.py my_manifest.json my_census

# 3. Solve all environments (run multiple workers in parallel)
poetry run python src/solve_census.py my_census

# 4. Report census status and list environments with completions
poetry run python src/analyze_census.py my_census
```

`generate_census.py` supports three pattern types:
- `-n <num_fingers>` — finger patterns (enumerated via octahedron face-pairing constraints)
- `-m <num_fingers>` — multi-component finger patterns (bracelets with complement symmetry)
- `-l <max_length>` — long cusp sequences

Patterns can be sorted by complexity (`-s compression` or `-s entropy`),
defaulting to least-complex first (use `-r` to reverse).

`construct_census.py` copies the manifest into the census directory as
`manifest.json`. When `solve_census.py` finds this file, it visits
environments in manifest order so earlier patterns are solved first.
Without a manifest, it falls back to filesystem directory order.

Multiple `solve_census.py` workers can run concurrently against the same
census directory — a file-based claiming protocol prevents duplicated work.

### Visualization

The `draw.py` module can render cusp tilings with embedding annotations using pycairo.

## Project structure

```
src/
  base.py                 Core data structures (cells, pairings, embeddings)
  construction.py         Cusp tiling, embedding collection, constraint propagation
  solver.py               Backtracking search with checkpoint/resume
  finger_cusp.py          Finger (short-meridian) cusp pattern constructor
  long_cusp.py            Long-meridian cusp pattern constructor
  bracelets.py            Bracelet/necklace enumeration (rotation, reflection, optional complement)
  binary_loop.py          Discrete calculus on cyclic binary (mod 2) sequences
  pattern_restriction.py  Short-meridian pattern enumeration via rank spectrum
  env.py                  Search environment I/O (config, state, checkpoints)
  construct.py            CLI: create a single search environment
  generate_census.py      CLI: enumerate patterns and write a census manifest
  construct_census.py     CLI: build environments from a census manifest
  solve.py                CLI: run the solver (supports stop/resume)
  solve_census.py         CLI: distributed worker that solves a census
  analyze.py              CLI: extract Regina isomorphism signatures
  analyze_census.py       CLI: report census status and completions
  export_regina.py        Convert cellulations to Regina triangulations
  draw.py                 Cusp visualization (pycairo)
  examples.py             Example cusp configurations
tests/
  test_base.py            Tests for core data structures
  test_construction.py    Tests for construction and constraint propagation
  test_finger_cusp.py     Tests for finger pattern generation
  test_long_cusp.py       Tests for long cusp pattern generation
```

## Testing

```sh
poetry run pytest tests/

```
## TODO

- Fix up and add more tests

## Author

Nick Jordan (njordan@d.umn.edu)
