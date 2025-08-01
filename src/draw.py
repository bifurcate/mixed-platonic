import cairo
import colorsys
import math

from base import (
  Sqr,
  Tri,
)
from construction import Construction


SQRT_3 = math.sqrt(3)
A = 0.5
B = SQRT_3/2

SQR_POS_VERTS =   ((0, 0), (0, 1), (1, 1), (1, 0))
TRI_A_POS_VERTS = ((0, 1), (A, 1 + B), (1, 1))
TRI_B_POS_VERTS = ((1, 1), (A, 1 + B), (1 + A, 1 + B))

SQR_NEG_VERTS =   ((A, 1 + B), (0, 1), (B, A), (A+B, A+B))
TRI_A_NEG_VERTS = ((0, 1), (0, 0), (B, A))
TRI_B_NEG_VERTS = ((B, A), (0, 0), (B, -A))


def count_pos_neg(finger_pattern, finger_idx):
  truncated_fp = finger_pattern[:finger_idx]
  return truncated_fp.count(1), truncated_fp.count(-1)

def show_centered_text(ctx, x, y, text):
  """Draw text centered at (x, y) in pycairo."""
  extents = ctx.text_extents(text)
  ctx.move_to(
    x - extents.width / 2 - extents.x_bearing,
    y - extents.height / 2 - extents.y_bearing
  )
  ctx.text_path(text)     # Convert text to path (respects CTM)
  ctx.set_source_rgb(0, 0, 0)
  ctx.fill()

def get_centroid(verts: tuple[tuple[int,int]]):
  n = len(verts)
  return (
    sum(p[0] for p in verts)/n,
    sum(p[1] for p in verts)/n,
  )

def nudge_to_centroid(point, centroid, nudge_factor=0.1):
  return (
    point[0] + nudge_factor * (centroid[0] - point[0]),
    point[1] + nudge_factor * (centroid[1] - point[1]),
  )

def distribute_indices(n):
    """Yield indices in an order that spreads them apart."""
    if n == 0:
        return []
    result = [0]
    step = n // 2
    while step:
        result += [i + step for i in result]
        step //= 2
    return result[:n]

def generate_spread_color_map(n, s=0.8, v=0.9):
    import colorsys
    colors = []
    order = distribute_indices(n)
    for i in order:
        hue = i / n
        rgb = colorsys.hsv_to_rgb(hue, s, v)
        colors.append(rgb)
    return colors

def draw_empty_poly_finger(
  ctx,
  offset,
  verts,
):
  ctx.save()

  ctx.translate(offset[0], offset[1])

  # draw cusp cell

  p = verts[0]
  ctx.move_to(p[0], p[1])

  for p in verts[1:]:
    ctx.line_to(p[0], p[1])
  
  ctx.close_path()
  ctx.set_source_rgb(0, 0, 0)  # black outline
  ctx.stroke()

  ctx.restore()

def draw_poly_finger_offset(
  ctx,
  offset,
  verts: tuple[tuple[int,int]],
  embedding_labels,
  color_map,
  color_idx,
):

  ctx.save()

  ctx.translate(offset[0], offset[1])

  # draw cusp cell

  p = verts[0]
  ctx.move_to(p[0], p[1])

  for p in verts[1:]:
    ctx.line_to(p[0], p[1])
  
  ctx.close_path()
  color = color_map[color_idx]
  ctx.set_source_rgb(color[0], color[1], color[2])
  ctx.fill_preserve()
  ctx.set_source_rgb(0, 0, 0)  # black outline
  ctx.stroke()

  # add labels

  ctx.set_source_rgb(0, 0, 0)

  centroid = get_centroid(verts)
  
  ctx.move_to(centroid[0], centroid[1])
  ctx.show_text(str(embedding_labels[0]))

  for i, p in enumerate(verts):
    p_ = nudge_to_centroid(p, centroid, 0.2)
    ctx.move_to(p_[0], p_[1])
    show_centered_text(ctx, p_[0], p_[1], str(embedding_labels[i+1]))

  ctx.restore()

def draw_finger_cell(
  ctx,
  construction: Construction,
  finger_pattern,
  finger_idx,
  knuckle_idx,
  color_map,
):
  
  finger_sign = finger_pattern[finger_idx]

  if knuckle_idx == 0:
    cusp_cell = Sqr(finger_idx)
    if finger_sign > 0:
      verts = SQR_POS_VERTS
    else:
      verts = SQR_NEG_VERTS

  elif knuckle_idx == 1:
    cusp_cell = Tri(2 * finger_idx)
    if finger_sign > 0:
      verts = TRI_A_POS_VERTS
    else:
      verts = TRI_A_NEG_VERTS

  elif knuckle_idx == 2:
    cusp_cell = Tri(2 * finger_idx + 1)
    if finger_sign > 0:
      verts = TRI_B_POS_VERTS
    else:
      verts = TRI_B_NEG_VERTS

  embedding = construction.embeddings.get_embedding_by_cusp_cell(cusp_cell)

  num_pos, num_neg = count_pos_neg(finger_pattern, finger_idx)

  cx = num_pos + B * num_neg
  cy = -A * num_neg

  if embedding is None:
    draw_empty_poly_finger(
      ctx,
      (cx, cy),
      verts,
    )
  else:
    if embedding.manifold_cell.is_tet():
      color_idx = embedding.manifold_cell.cell_index
    else:
      color_idx = construction.num_tets + embedding.manifold_cell.cell_index

    embedding_labels = embedding.embedding_spec

    draw_poly_finger_offset(
      ctx,
      (cx, cy),
      verts,
      embedding_labels,
      color_map,
      color_idx
  )

def draw_finger(
  ctx,
  construction,
  finger_pattern,
  finger_idx,
  color_map
):
  for knuckle_idx in range(3):
    draw_finger_cell(
      ctx,
      construction,
      finger_pattern,
      finger_idx,
      knuckle_idx,
      color_map
    )

def draw_stack(finger_pattern, construction, output_filename):
  
  WIDTH, HEIGHT = 2048, 1024

  if output_filename.endswith('svg'):
    cairo_surface = cairo.SVGSurface(output_filename, WIDTH, HEIGHT)
  elif output_filename.endswith('png'):
    cairo_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
  else:
    raise ValueError("Unsupported file format. Use .svg or .png")
  
  ctx = cairo.Context(cairo_surface)

  ctx.set_line_width(.01)
  ctx.translate(100,512)
  ctx.scale(1, -1)
  ctx.scale(100,100)

  ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
  ctx.set_font_size(.15)
  font_matrix = cairo.Matrix(xx=.15, yx=0, xy=0, yy=-.15, x0=0, y0=0)
  ctx.set_font_matrix(font_matrix)

  n = len(finger_pattern)
  color_map = generate_spread_color_map(construction.num_tets + construction.num_octs, s=0.8, v=0.9)

  for i in range(n):
    draw_finger(
      ctx,
      construction,
      finger_pattern,
      i,
      color_map,
    )
  
  if output_filename.endswith(".png"):
    cairo_surface.write_to_png(output_filename)
  else:
    cairo_surface.finish()