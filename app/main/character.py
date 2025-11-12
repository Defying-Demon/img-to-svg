import math
import random
from typing import List, Optional, Tuple

# Predefined color palettes
FILL_COLORS = [
    "#CEE5D0",
    "#ff8080",
    "#79B4B7",
    "#6B7AA1",
    "#DEBA9D",
    "#F6AE99",
    "#FFBCBC",
    "#B5EAEA",
    "#CEE5D0",
    "#c0dba9",
    "#b8e0b6",
    "#9A8194",
    "#d8db76",
    "#E8E9A1",
    "#ECB390",
    "#CFDAC8",
    "#f0c0c0",
    "#E5EDB7",
    "#F6DEF6",
]

BACKGROUND_COLORS = [
    "#FAF4EF",
    "#EFFAEF",
    "#EFF4FA",
    "#FAEFFA",
    "#EFF4FA",
    "#F4EFFA",
    "#FAFAEF",
    "#FAEFF4",
    "#EFFAFA",
    "#EFF7EB",
    "#DBDBDB",
    "#EDF1F7",
    "#EFF7EB",
    "#F7F7E9",
    "#EFEFEF",
]


def divide_circle(count: int) -> List[int]:
    """Divide the circle evenly by count and return a list of angles in degrees."""
    deg_step = 360 / count
    return [int(i * deg_step) for i in range(count)]


def random_radius(val: float, min_val: float, max_val: float) -> float:
    """Generate a random radius between min_val and max_val, scaled by val."""
    radius = min_val + val * (max_val - min_val)
    if radius > max_val:
        radius = radius - min_val
    elif radius < min_val:
        radius = min_val
    return radius


def polar_to_cartesian(
    center: float, radius: float, angle_deg: float
) -> Tuple[int, int]:
    """Converts polar coordinates to cartesian."""
    angle_rad = math.radians(angle_deg)
    x = center + radius * math.cos(angle_rad)
    y = center + radius * math.sin(angle_rad)
    return round(x), round(y)


def generate_shape_points(
    size: float, min_growth: float, edges_num: int
) -> List[Tuple[int, int]]:
    """Generate outer shape points for the character."""
    center = size / 2
    outer_radius = center
    inner_radius = min_growth * (outer_radius / 10)

    angles = divide_circle(edges_num)
    points = []

    for angle in angles:
        radius = random_radius(random.uniform(0.1, 1.1), inner_radius, outer_radius)
        pt = polar_to_cartesian(center, radius, angle)
        points.append(pt)
    return points


def create_svg_path(points: List[Tuple[int, int]]) -> str:
    """Create an SVG path data using quadratic curves between points."""
    if len(points) < 3:
        return ""
    svg_path = ""

    # Move to midpoint between first and second points
    mid_x = (points[0][0] + points[1][0]) / 2
    mid_y = (points[0][1] + points[1][1]) / 2
    svg_path += f"M{mid_x},{mid_y}"

    for i in range(len(points)):
        p1 = points[(i + 1) % len(points)]
        p2 = points[(i + 2) % len(points)]
        mid = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
        svg_path += f" Q{p1[0]},{p1[1]} {mid[0]},{mid[1]}"
    svg_path += " Z"
    return svg_path


def draw_eyes(size: float, eye_type: Optional[str], blink_speed: float) -> str:
    """Randomly draws one or two eyes."""
    rand_val = random.randint(0, 9)
    offset_x = random.uniform(-2, 2)
    offset_y = random.uniform(-2, 2)

    pupil_r = size / 2 if eye_type == "single" else round(random.uniform(3, size / 3))
    blink_anim = f"<animate attributeName='r' values='{pupil_r};1;{pupil_r}' dur='{blink_speed}s' repeatCount='indefinite' />"

    # Generate the eyes based on the random number
    if eye_type == "single" or (eye_type is None and rand_val < 5):
        return f"""
        <g id='eye' transform='translate(50, 50)'>
            <circle id='iris' cx='0' cy='0' r='{size}' stroke='#000' stroke-width='2' fill='#fff' />
            <circle id='pupil' cx='{offset_x}' cy='{offset_y}' r='{pupil_r}' fill='#000'>{blink_anim}</circle>
        </g>"""
    else:
        return f"""
        <g>
            <g transform = 'translate(38, 50)'>
                <circle cx='0' cy='0' r='{size}' stroke='#000' stroke-width='2' fill='#fff' />
                <circle cx='{offset_x}' cy='{offset_y}' r='{round(random.uniform(3, size / 3))}' fill='#000'>{blink_anim}</circle>
            </g>
            <g transform = 'translate(58, 50)'>
                <circle cx='0' cy='0' r='{size}' stroke='#000' stroke-width='2' fill='#fff' />
                <circle cx='{offset_x}' cy='{offset_y}' r='{round(random.uniform(3, size / 3))}' fill='#000'>{blink_anim}</circle>
            </g>
        </g>"""


def generate_character_svg(
    edges: int = 7,
    growth: float = 5.0,
    eye_type: Optional[str] = None,
    rotate_speed: float = 3.0,
    blink_speed: float = 2.0,
    fill: Optional[str] = None,
    bg: Optional[str] = None,
) -> str:
    """Generates a complete SVG for a character."""
    edges = max(6, min(10, int(edges)))
    growth = max(1.0, min(10.0, float(growth)))
    rotate_speed = max(0.5, float(rotate_speed))
    blink_speed = max(0.5, float(blink_speed))

    size = random.uniform(95, 105)
    eye_size = random.uniform(6, 10)
    fill_color = fill if fill and fill.startswith("#") else random.choice(FILL_COLORS)
    background_color = (
        bg if bg and bg.startswith("#") else random.choice(BACKGROUND_COLORS)
    )

    points = generate_shape_points(size, growth, edges)
    path_data = create_svg_path(points)
    eyes_svg = draw_eyes(eye_size, eye_type, blink_speed)

    # Compliling various parts
    header = "<svg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg' width='500' height='500'>"
    footer = "</svg>"
    background = (
        f"<rect x='0' y='0' width='100' height='100' fill='{background_color}' />"
    )
    body = f"""
    <path stroke='transparent' stroke-width='0' fill='{fill_color}' d='{path_data}'>
        <animateTransform attributeName='transform' type='rotate' values='-2 50 50;2 50 50;-2 50 50' dur='{rotate_speed}s' repeatCount='indefinite'/>
    </path>"""
    outline = f"<path transform='translate(-3, -3)' stroke='#000' stroke-width='2' fill='none' d='{path_data}' />"
    blush = f"""
    <g>
        <circle transform="translate(70, 65)" cx="0" cy="0" r="6" fill="rgba(255, 255, 255, 0.3)">
            <animate attributeName='fill-opacity' vvalues="0.3;0.8;0.3" dur="{blink_speed}s" repeatCount="indefinite"/>
        </circle>
        <circle transform="translate(30, 65)" cx="0" cy="0" r="6" fill="rgba(255, 255, 255, 0.3)">
            <animate attributeName='fill-opacity' vvalues="0.3;0.8;0.3" dur="{blink_speed}s" repeatCount="indefinite"/>
        </circle>
    </g>"""

    # Join all svg parts
    complete_svg = (
        f"{header}\n{background}\n{body}\n{blush}\n{outline}\n{eyes_svg}\n{footer}"
    )
    return complete_svg


if __name__ == "__main__":
    svg_content = generate_character_svg()
    with open("character.svg", "w", encoding="utf-8") as fp:
        fp.write(svg_content)
    print("[INFO]: Character saved in 'character.svg'")
