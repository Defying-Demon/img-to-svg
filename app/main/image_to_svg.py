import cv2
import numpy as np
import potrace


def load_image(filepath):
    """Load image and convert to RGB."""
    image_bgr = cv2.imread(filepath)
    if image_bgr is None:
        raise FileNotFoundError(f"Could not load image at {filepath}")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return image_rgb


def quantize_image(image, K=6):
    """Run K-means on image and return centers and 2D labels."""
    h, w, _ = image.shape
    data = image.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
    _compactness, labels, centers = cv2.kmeans(
        data, K, None, criteria, 5, cv2.KMEANS_PP_CENTERS
    )
    centers = np.uint8(centers)
    labels_2D = labels.reshape(h, w)
    print(f"K-means done. K={K}. Centers shape: {centers.shape}")
    return centers, labels_2D


# --- Potrace helpers ---------------------------------------------------------


def _curve_to_path_d(curve):
    """
    Convert a potrace Curve (and its children) into a single SVG 'd' string.
    IMPORTANT: we append children subpaths into the SAME 'd' so even-odd fill works.
    """
    parts = []

    def append_curve(c):
        # start point
        sx, sy = c.start_point  # (x, y)
        parts.append(f"M {sx} {sy}")
        # segments
        for seg in c:  # you can also use c.segments
            if seg.is_corner:
                cx, cy = seg.c
                ex, ey = seg.end_point
                # two straight lines via one 'L' with two coords is valid SVG
                parts.append(f"L {cx} {cy} {ex} {ey}")
            else:
                (c1x, c1y) = seg.c1
                (c2x, c2y) = seg.c2
                ex, ey = seg.end_point
                parts.append(f"C {c1x} {c1y} {c2x} {c2y} {ex} {ey}")
        parts.append("Z")
        # recurse into holes/children
        for child in c.children:
            append_curve(child)

    append_curve(curve)
    return " ".join(parts)


def _trace_mask_to_svg_paths(
    mask_u8,
    fill_color,
    turdsize=2,
    turnpolicy=potrace.TURNPOLICY_MINORITY,
    alphamax=1.0,
    opticurve=True,
    opttolerance=0.2,
):
    """
    Trace a binary mask with potrace and emit SVG <path> elements.
    """
    # Potrace reads any nonzero as foreground. Use {0,1} and a contiguous array.
    data = np.ascontiguousarray((mask_u8 > 0).astype(np.uint8))

    # Trace; returns a Path (collection of Curves with possible nesting).
    path = potrace.Bitmap(data).trace(
        turdsize=turdsize,
        turnpolicy=turnpolicy,
        alphamax=alphamax,
        opticurve=opticurve,
        opttolerance=opttolerance,
    )

    body = []
    # Only iterate top-level curves; children are handled inside _curve_to_path_d.
    for curve in path.curves_tree:
        d = _curve_to_path_d(curve)
        body.append(f'<path d="{d}" fill="{fill_color}" stroke="none"/>')
    return "\n".join(body)


def image_to_svg(filepath: str, K: int = 6):
    """Build SVG header + traced clusters (properly handling holes)."""
    image = load_image(filepath)
    centers, labels_2D = quantize_image(image, K)
    height, width = image.shape[:2]
    header = (
        f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
    )

    body = ['<g fill-rule="evenodd">']  # even-odd handles holes regardless of winding

    cluster_areas = [
        (idx, int((labels_2D == idx).sum())) for idx in range(len(centers))
    ]
    for cluster_idx, _area in sorted(cluster_areas, key=lambda t: -t[1]):
        mask = (labels_2D == cluster_idx).astype(np.uint8)
        if mask.sum() == 0:
            continue

        r, g, b = map(int, centers[cluster_idx])
        color = f"rgb({r},{g},{b})"

        # 255-scale is fine, but Potrace only cares about nonzero; keep as 0/255 for clarity
        mask_u8 = (mask * 255).astype(np.uint8)

        body.append(_trace_mask_to_svg_paths(mask_u8, color))

    body.append("</g>\n</svg>")
    svg = header + "\n".join(body)
    return svg


if __name__ == "__main__":
    svg_content = image_to_svg("data/sample_image.jpg", K=6)

    # write the svg to file
    output_file = "image_svg.svg"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[INFO]: SVG written to {output_file}")
