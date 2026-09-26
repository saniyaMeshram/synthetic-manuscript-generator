import io
import os
import random
import zipfile

from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/generate", methods=["POST"])
def generate():

    print("GENERATE ENDPOINT CALLED")

    data = request.get_json()

    if not data:
        return {
            "success": False,
            "message": "No data received."
        }, 400

    text = data.get("text", "").strip()
    script = data.get("script", "").strip()

    if not text:
        return {
            "success": False,
            "message": "Text is required."
        }, 400

    if script not in ["devanagari", "modi", "sharada"]:
        return {
            "success": False,
            "message": "Invalid script."
        }, 400

    print("Script:", script)
    print("Text:", text)

    # --------------------------------
    # Font selection
    # --------------------------------

    font_paths = {
        "devanagari": "fonts/NotoSansDevanagari-Regular.ttf",
        "modi": "fonts/NotoSansModi-Regular.ttf",
        "sharada": "fonts/Sharada-Regular.ttf"
    }

    font_path = font_paths[script]

    if not os.path.exists(font_path):
        return {
            "success": False,
            "message": f"Font not found: {font_path}"
        }, 500

    # --------------------------------
    # Create aged paper background
    # --------------------------------

    width = 1600
    height = 2200

    image = Image.new(
        "RGB",
        (width, height),
        (224, 207, 170)
    )

    draw = ImageDraw.Draw(image)

    # Add paper noise
    for _ in range(30000):

        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        shade = random.randint(170, 225)

        draw.point(
            (x, y),
            fill=(shade, shade - 15, shade - 35)
        )

    # --------------------------------
    # Load font
    # --------------------------------

    font_size = 48

    print("Font path:", font_path)
    print("Font exists:", os.path.exists(font_path))

    try:
        font = ImageFont.truetype(
            font_path,
            font_size,
            layout_engine=ImageFont.Layout.RAQM
        )
        print("FONT LOADED SUCCESSFULLY")

        # Test one character only
        test_char = text[0]

        print("Testing character:", repr(test_char))

        bbox = draw.textbbox(
            (0, 0),
            test_char,
            font=font
        )

        print("CHARACTER RENDER TEST SUCCESS:", bbox)

    except Exception as e:
        print("SHARADA FONT/RENDER ERROR:", repr(e))

        return {
            "success": False,
            "message": f"Sharada rendering failed: {str(e)}"
        }, 500

    # --------------------------------
    # Draw text
    # --------------------------------

    margin_x = 140
    margin_y = 180

    max_width = width - (margin_x * 2)

    lines = []

    # Break input into lines
    for paragraph in text.split("\n"):

        words = paragraph.split()
        current_line = ""

        for word in words:

            test_line = (
                current_line + " " + word
            ).strip()

            bbox = draw.textbbox(
                (0, 0),
                test_line,
                font=font
            )

            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)

                current_line = word

        if current_line:
            lines.append(current_line)

        lines.append("")

    # --------------------------------
    # Render text
    # --------------------------------

    y = margin_y

    for line in lines:

        if y > height - 150:
            break

        draw.text(
            (margin_x, y),
            line,
            font=font,
            fill=(55, 38, 25)
        )

        y += 75

    # --------------------------------
    # Save image in memory
    # --------------------------------

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    # --------------------------------
    # Create Markdown
    # --------------------------------

    markdown_content = text

    # --------------------------------
    # Create ZIP
    # --------------------------------

    zip_bytes = io.BytesIO()

    with zipfile.ZipFile(
        zip_bytes,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        zip_file.writestr(
            "manuscript.png",
            image_bytes.getvalue()
        )

        zip_file.writestr(
            "manuscript.md",
            markdown_content
        )

    zip_bytes.seek(0)

    print("Generation completed.")

    return send_file(
        zip_bytes,
        mimetype="application/zip",
        as_attachment=True,
        download_name="manuscript.zip"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)