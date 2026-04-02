import pytest

from construction import Cusp, Embeddings, Construction
from finger_cusp import FingerCuspGenerator
from solver import Solver, StackFrame

FINGER_PATTERN = [1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1]
NUM_TETS = 6
NUM_OCTS = 2


def make_solver():
    """Build a Solver for the Boyd finger pattern."""
    cusp = Cusp()
    gen = FingerCuspGenerator(cusp, FINGER_PATTERN)
    cusp = gen.generate()
    traversal = list(gen.traversal())
    embeddings = Embeddings()
    construction = Construction(cusp, embeddings)
    return Solver(traversal, construction, NUM_TETS, NUM_OCTS), traversal


def test_solver_completes():
    """Full run finds the expected number of completions."""
    solver, _ = make_solver()
    result = solver.run()

    assert result == "completed"
    assert solver.counter == 47817
    assert len(solver.completed) == 1


def test_solver_stop_and_resume():
    """Stopping mid-search and resuming produces the same results as a full run."""
    # Full run for reference
    solver_full, traversal = make_solver()
    solver_full.run()

    # Partial run: stop after 10000 iterations
    solver_partial, _ = make_solver()

    original_add = solver_partial.construction.embeddings.add_embedding

    def stop_after_n(embedding):
        original_add(embedding)
        if solver_partial.counter >= 10000:
            solver_partial.request_stop()

    solver_partial.construction.embeddings.add_embedding = stop_after_n

    result = solver_partial.run()
    assert result == "stopped"
    assert solver_partial.counter >= 10000
    assert len(solver_partial.stack) > 0

    # Save checkpoint
    checkpoint = solver_partial.save_checkpoint()
    assert len(checkpoint["stack"]) > 0
    assert checkpoint["counter"] == solver_partial.counter

    # Resume from checkpoint
    solver_resumed, _ = make_solver()
    solver_resumed.load_checkpoint(checkpoint)
    assert solver_resumed.counter == solver_partial.counter

    result = solver_resumed.run()
    assert result == "completed"
    assert solver_resumed.counter == solver_full.counter
    assert len(solver_resumed.completed) == len(solver_full.completed)
    for c_resumed, c_full in zip(solver_resumed.completed, solver_full.completed):
        assert c_resumed == c_full


def test_solver_multiple_stops():
    """Multiple stop/resume cycles produce the same final result."""
    solver_full, _ = make_solver()
    solver_full.run()

    stop_points = [5000, 15000, 30000]
    checkpoint = None

    for stop_at in stop_points:
        solver, _ = make_solver()
        if checkpoint is not None:
            solver.load_checkpoint(checkpoint)

        original_add = solver.construction.embeddings.add_embedding

        def stop_after_n(embedding, s=solver, n=stop_at):
            original_add(embedding)
            if s.counter >= n:
                s.request_stop()

        solver.construction.embeddings.add_embedding = stop_after_n

        result = solver.run()
        assert result == "stopped"
        checkpoint = solver.save_checkpoint()

    # Final resume to completion
    solver_final, _ = make_solver()
    solver_final.load_checkpoint(checkpoint)
    result = solver_final.run()

    assert result == "completed"
    assert solver_final.counter == solver_full.counter
    assert len(solver_final.completed) == len(solver_full.completed)


def test_solver_immediate_stop():
    """Stopping before any work is done can be resumed."""
    solver, _ = make_solver()
    solver.request_stop()

    result = solver.run()
    assert result == "stopped"
    assert solver.counter == 0

    checkpoint = solver.save_checkpoint()
    assert len(checkpoint["stack"]) == 1

    solver_resumed, _ = make_solver()
    solver_resumed.load_checkpoint(checkpoint)
    result = solver_resumed.run()

    assert result == "completed"
    assert solver_resumed.counter == 47817
    assert len(solver_resumed.completed) == 1


def test_checkpoint_serialization_roundtrip():
    """Checkpoint data survives JSON serialization (tuples become lists)."""
    import json

    solver, _ = make_solver()

    original_add = solver.construction.embeddings.add_embedding

    def stop_after_n(embedding):
        original_add(embedding)
        if solver.counter >= 1000:
            solver.request_stop()

    solver.construction.embeddings.add_embedding = stop_after_n
    solver.run()

    checkpoint = solver.save_checkpoint()

    # Simulate JSON round-trip (tuples -> lists)
    serialized = json.dumps(checkpoint)
    deserialized = json.loads(serialized)

    solver_resumed, _ = make_solver()
    solver_resumed.load_checkpoint(deserialized)
    result = solver_resumed.run()

    assert result == "completed"
    assert solver_resumed.counter == 47817
    assert len(solver_resumed.completed) == 1


def test_stack_frame_dump_load():
    """StackFrame round-trips through dump/load."""
    from base import Sqr, OctSqrEmbedding, Oct

    cusp_cell = Sqr(0)
    embedding = OctSqrEmbedding(Oct(0), Sqr(0), (0, 1, 2, 3, 4, 5))
    induced = [OctSqrEmbedding(Oct(1), Sqr(1), (0, 1, 2, 3, 4, 5))]

    frame = StackFrame(
        cusp_cell=cusp_cell,
        embedding=embedding,
        induced_embeddings=induced,
        init=True,
    )

    data = frame.dump()
    restored = StackFrame.load(data)

    assert restored.cusp_cell == frame.cusp_cell
    assert restored.embedding == frame.embedding
    assert restored.induced_embeddings == frame.induced_embeddings
    assert restored.init == frame.init
    assert restored.placed is False


def test_stack_frame_dump_load_none_embedding():
    """StackFrame with no embedding round-trips correctly."""
    from base import Tri

    frame = StackFrame(cusp_cell=Tri(3))

    data = frame.dump()
    restored = StackFrame.load(data)

    assert restored.cusp_cell == frame.cusp_cell
    assert restored.embedding is None
    assert restored.induced_embeddings == []
    assert restored.init is False
