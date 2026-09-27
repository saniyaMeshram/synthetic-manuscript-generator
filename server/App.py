import io
import os
import random
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

ROOT = Path(__file__).resolve().parent


# ============================================================
# CORS
# ============================================================

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    }
)


# ============================================================
# FONT PATHS
# ============================================================

FONT_PATHS = {
    "devanagari": ROOT / "fonts" / "NotoSansDevanagari-Regular.ttf",
    "modi": ROOT / "fonts" / "NotoSansModi-Regular.ttf",
    "sharada": ROOT / "fonts" / "Sharada-Regular.ttf"
}


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def hello_world():
    return "<p>Hello, World!</p>"


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "message": "Synthetic Manuscript Generator backend is running."
    })


# ============================================================
# GENERATE MANUSCRIPT
# ============================================================

# IMPORTANT:
# Only POST is declared here.
# Flask-CORS handles OPTIONS automatically.
@app.route("/generate", methods=["POST"])
def generate():

    print("\n" + "=" * 60)
    print("GENERATE ENDPOINT CALLED")
    print("=" * 60)

    # --------------------------------------------------------
    # Read JSON
    # --------------------------------------------------------

    try:
        data = request.get_json(silent=True)
    except Exception as e:

        print("JSON ERROR:", repr(e))

        return jsonify({
            "success": False,
            "message": "Invalid JSON request."
        }), 400

    if not data:

        print("No data received.")

        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    text = str(
        data.get("text", "")
    ).strip()

    script = str(
        data.get("script", "")
    ).strip().lower()

    print("Script:", script)
    print("Text:", text)

    # --------------------------------------------------------
    # Validate text
    # --------------------------------------------------------

    if not text:

        return jsonify({
            "success": False,
            "message": "Text is required."
        }), 400

    # --------------------------------------------------------
    # Validate script
    # --------------------------------------------------------

    if script not in FONT_PATHS:

        return jsonify({
            "success": False,
            "message": (
                "Invalid script. "
                "Choose devanagari, modi, or sharada."
            )
        }), 400

    # --------------------------------------------------------
    # Font
    # --------------------------------------------------------

    font_path = FONT_PATHS[script]

    print("Font path:", font_path)
    print("Font exists:", font_path.exists())

    if not font_path.exists():

        return jsonify({
            "success": False,
            "message": f"Font not found: {font_path}"
        }), 500

    # --------------------------------------------------------
    # Image dimensions
    # --------------------------------------------------------

    width = 1600
    height = 2200

    # --------------------------------------------------------
    # Create paper
    # --------------------------------------------------------

    image = Image.new(
        "RGB",
        (width, height),
        (224, 207, 170)
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # Paper texture
    # --------------------------------------------------------

    for _ in range(30000):

        x = random.randint(
            0,
            width - 1
        )

        y = random.randint(
            0,
            height - 1
        )

        shade = random.randint(
            170,
            225
        )

        draw.point(
            (x, y),
            fill=(
                shade,
                max(0, shade - 15),
                max(0, shade - 35)
            )
        )

    # --------------------------------------------------------
    # Load font
    # --------------------------------------------------------

    font_size = 48

    print("Loading font...")

    try:

        font = ImageFont.truetype(
            str(font_path),
            font_size,
            layout_engine=ImageFont.Layout.RAQM
        )

        print("FONT LOADED SUCCESSFULLY")

    except Exception as e:

        print(
            "FONT ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message": (
                f"Font loading failed: {str(e)}"
            )
        }), 500

    # --------------------------------------------------------
    # Test rendering
    # --------------------------------------------------------

    try:

        test_char = text[0]

        bbox = draw.textbbox(
            (0, 0),
            test_char,
            font=font
        )

        print(
            "CHARACTER RENDER TEST SUCCESS:",
            repr(test_char),
            bbox
        )

    except Exception as e:

        print(
            "CHARACTER RENDER ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message": (
                f"Character rendering failed: {str(e)}"
            )
        }), 500

    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    margin_x = 140
    margin_y = 180

    max_width = width - (
        margin_x * 2
    )

    line_spacing = 85

    lines = []

    # --------------------------------------------------------
    # Break text into lines
    # --------------------------------------------------------

    paragraphs = text.split("\n")

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:

            lines.append("")
            continue

        words = paragraph.split()

        current_line = ""

        for word in words:

            if current_line:

                test_line = (
                    current_line
                    + " "
                    + word
                )

            else:

                test_line = word

            bbox = draw.textbbox(
                (0, 0),
                test_line,
                font=font
            )

            line_width = (
                bbox[2] - bbox[0]
            )

            if line_width <= max_width:

                current_line = test_line

            else:

                if current_line:

                    lines.append(
                        current_line
                    )

                current_line = word

        if current_line:

            lines.append(
                current_line
            )

        lines.append("")

    # --------------------------------------------------------
    # Draw text
    # --------------------------------------------------------

    y = margin_y

    for line in lines:

        if y > height - 180:
            break

        if line:

            x_offset = random.randint(
                -3,
                3
            )

            draw.text(
                (
                    margin_x + x_offset,
                    y
                ),
                line,
                font=font,
                fill=(
                    55,
                    38,
                    25
                )
            )

        y += line_spacing

    # --------------------------------------------------------
    # Manuscript border
    # --------------------------------------------------------

    draw.rectangle(
        (
            60,
            60,
            width - 60,
            height - 60
        ),
        outline=(
            105,
            78,
            48
        ),
        width=5
    )

    draw.rectangle(
        (
            80,
            80,
            width - 80,
            height - 80
        ),
        outline=(
            145,
            115,
            75
        ),
        width=2
    )

    # --------------------------------------------------------
    # PNG
    # --------------------------------------------------------

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    png_data = image_bytes.getvalue()

    print(
        "PNG generated:",
        len(png_data),
        "bytes"
    )

    # --------------------------------------------------------
    # Markdown
    # --------------------------------------------------------

    markdown_content = (
        "# Synthetic Manuscript Annotation\n\n"
        f"**Script:** {script}\n\n"
        "**Text:**\n\n"
        f"{text}\n"
    )

    # --------------------------------------------------------
    # ZIP
    # --------------------------------------------------------

    zip_bytes = io.BytesIO()

    with zipfile.ZipFile(
        zip_bytes,
        mode="w",
        compression=zipfile.ZIP_DEFLATED
    ) as zip_file:

        zip_file.writestr(
            "manuscript.png",
            png_data
        )

        zip_file.writestr(
            "manuscript.md",
            markdown_content
        )

    zip_bytes.seek(0)

    print(
        "ZIP generated successfully."
    )

    print(
        "Generation completed."
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Return ZIP
    # --------------------------------------------------------

    return send_file(
        zip_bytes,
        mimetype="application/zip",
        as_attachment=True,
        download_name="manuscript.zip"
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "message": "Endpoint not found."
    }), 404


@app.errorhandler(500)
def internal_error(error):

    print(
        "INTERNAL SERVER ERROR:",
        repr(error)
    )

    return jsonify({
        "success": False,
        "message": "Internal server error."
    }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print(
        "SYNTHETIC MANUSCRIPT GENERATOR BACKEND"
    )
    print("=" * 60)

    print(
        "Project root:",
        ROOT
    )

    print(
        "Font directory:",
        ROOT / "fonts"
    )

    for script_name, path in FONT_PATHS.items():

        print(
            f"{script_name}:",
            "FOUND"
            if path.exists()
            else "NOT FOUND",
            path
        )

    print("=" * 60)

    print(
        "Backend URL: http://127.0.0.1:5000"
    )

    print(
        "Frontend URL: http://localhost:5173"
    )

    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )