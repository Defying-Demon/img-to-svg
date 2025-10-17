import cv2
import numpy as np
from PIL import Image

import potrace

def load_image(filename):
    """Load image and convert to RGB."""
    image_bgr = cv2.imread(filename)
    if image_bgr is None:
        raise FileNotFoundError(f"Could not load image at {filename}")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    print("Loaded image:", filename, "Shape:", image_rgb.shape)
    return image_rgb


def quantize_image(image, K=6, debug=False):
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

    if debug:
        quantized_image = centers[labels.flatten()].reshape(image.shape)
        try:
            Image.fromarray(quantized_image).show()
        except Exception:
            print("[WARNING]: It seems you are using headless environment.")
            pass  # headless environments
    
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


def _trace_mask_to_svg_paths(mask_u8, fill_color,
                             turdsize=2, turnpolicy=potrace.TURNPOLICY_MINORITY,
                             alphamax=1.0, opticurve=True, opttolerance=0.2):
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


# --- SVG assembly ------------------------------------------------------------

def build_svg(image_shape, centers, labels_2D):
    """Build SVG header + traced clusters (properly handling holes)."""
    height, width = image_shape[0], image_shape[1]
    header = (
        f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
    )

    body = ['<g fill-rule="evenodd">']  # even-odd handles holes regardless of winding


    cluster_areas = [(idx, int((labels_2D == idx).sum())) for idx in range(len(centers))]
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
    return header + "\n".join(body)

def write_svg(svg_content, output_file="output.svg"):
    """Write SVG to file."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[INFO]: SVG written to {output_file}")

def main(filename, K=6, debug=False):
    """Full pipeline."""
    image = load_image(filename)
    centers, labels_2D = quantize_image(image, K, debug=debug)
    svg_content = build_svg(image.shape, centers, labels_2D)
    write_svg(svg_content)


if __name__ == "__main__":
    main("data/sample_image.jpg", K=3, debug=True)
    # main("/home/sanjeev/pan_nepali.png", K=10, debug=False)
