# app/main/routes.py
import io
import os

from flask import current_app, render_template, request, send_file
from werkzeug.utils import secure_filename

from . import bp
from .character import generate_character_svg
from .image_to_svg import image_to_svg

ALLOWED_EXT = {"png", "jpg", "jpeg", "bmp", "gif"}


def allowed_file(f):
    return "." in f and f.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@bp.route("/character", methods=["GET", "POST"])
def character():
    params = {
        "edges": request.form.get("edges", 7, int),
        "growth": request.form.get("growth", 5.0, float),
        "eye_type": request.form.get("eye_type"),
        "rotate_speed": request.form.get("rotate_speed", 3.0, float),
        "blink_speed": request.form.get("blink_speed", 2.0, float),
        "fill": request.form.get("fill"),
        "bg": request.form.get("bg"),
    }
    svg = generate_character_svg(**params)
    return render_template("character.html", svg=svg, params=params)


@bp.route("/image-to-svg", methods=["GET", "POST"])
def img_to_svg():
    svg = None
    error = None
    if request.method == "POST":
        if "image" not in request.files:
            error = "No file selected"
        else:
            file = request.files["image"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(path)
                try:
                    K = int(request.form.get("k_clusters", 6))
                    svg = image_to_svg(path, K)
                except Exception as e:
                    error = f"Error: {e}"
            else:
                error = "Unsupported file type"
    return render_template("image_to_svg.html", svg=svg, error=error)


@bp.route("/download/character")
def download_char():
    params = {
        k: request.args.get(k)
        for k in [
            "edges",
            "growth",
            "eye_type",
            "rotate_speed",
            "blink_speed",
            "fill",
            "bg",
        ]
    }
    svg = generate_character_svg(**{k: v for k, v in params.items() if v})
    buffer = io.BytesIO(svg.encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="character.svg",
        mimetype="image/svg+xml",
    )
