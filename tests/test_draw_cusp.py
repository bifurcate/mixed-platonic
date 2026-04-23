from base import Tet, Tri
from construction import (
    Construction,
    Cusp,
    Embeddings,
    TetTriEmbedding,
)
from draw_cusp import draw_cusp
from finger_cusp import FingerCuspConstructor


FINGER_PATTERN = [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0]


def make_empty_setup():
    """Build a geometry + construction with no embeddings."""
    cusp = Cusp()
    constructor = FingerCuspConstructor(cusp, FINGER_PATTERN)
    cusp = constructor.generate()
    geo = constructor.cusp_geometry()
    embeddings = Embeddings()
    construction = Construction(cusp, embeddings, None, 6, 2)
    return geo, construction


def test_draw_cusp_tex_empty_cusp_structure(tmp_path):
    geo, construction = make_empty_setup()
    out = tmp_path / "cusp.tex"

    draw_cusp(geo, construction, str(out))

    text = out.read_text()
    assert text.count("\\begin{tikzpicture}") == 1
    assert text.count("\\end{tikzpicture}") == 1
    # Empty cusp: every complete cell drawn as an outline, none filled.
    assert "\\draw[line width=" in text
    assert "\\filldraw" not in text
    assert "\\node[" not in text


def test_draw_cusp_tex_with_embedding_has_labels(tmp_path):
    geo, construction = make_empty_setup()
    # One embedding (tet 0 → triangle 0) is enough to exercise fill,
    # corner/centroid labels, and the manifold/cusp tag lines.
    construction.embeddings.add_embedding(
        TetTriEmbedding(Tet(0), Tri(0), (0, 1, 2, 3))
    )

    out = tmp_path / "cusp.tex"
    draw_cusp(geo, construction, str(out))

    text = out.read_text()
    assert "\\filldraw[fill={rgb,1:red," in text
    assert "\\node[font=\\footnotesize]" in text
    assert "\\node[font=\\scriptsize]" in text
    assert "TET[0]" in text
    assert "TRI[0]" in text


def test_draw_cusp_png_still_works(tmp_path):
    """Cairo path should keep working after the tikz refactor."""
    geo, construction = make_empty_setup()
    out = tmp_path / "cusp.png"

    draw_cusp(geo, construction, str(out))

    assert out.is_file()
    assert out.stat().st_size > 0
