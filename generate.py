from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import argparse
import zipfile

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "dataset"
FONT_DIR = ROOT / "server" / "fonts"

SCRIPTS = {
    "devanagari": {
        "font_names": [
            "NotoSansDevanagari-Regular.ttf",
            "NotoSansDevanagari.ttf"
        ],
        "text": [
            "???? ?????? ???",
            "?????? ?????? ?????",
            "??????? ????",
            "????? ?????? ??????",
            "?????? ???? ????"
        ]
    },
    "modi": {
        "font_names": [
            "NotoSansModi-Regular.ttf",
            "NotoSansModi.ttf",
            "Modi.ttf"
        ],
        "text": [
            "???? ?????? ???",
            "?????? ?????? ?????",
            "??????? ????",
            "?????? ???? ????"
        ]
    },
    "sharada": {
        "font_names": [
            "Sharada.ttf",
            "Sharada-Regular.ttf"
        ],
        "text": [
            "???? ?????? ???",
            "?????? ?????? ?????",
            "??????? ????",
            "?????? ???? ????"
        ]
    }
}


def find_font(script):
    for name in SCRIPTS[script]["font_names"]:
        p = FONT_DIR / name
        if p.exists():
            return p

    candidates = list(FONT_DIR.glob("*.ttf"))
    if candidates:
        return candidates[0]

    raise FileNotFoundError(
        f"No .ttf font found in {FONT_DIR}"
    )


def create_background(width=700, height=950):
    base = Image.new("RGB", (width, height), (225, 210, 180))
    noise = Image.effect_noise((width, height), 12).convert("RGB")
    img = Image.blend(base, noise, 0.08)

    draw = ImageDraw.Draw(img)

    for _ in range(25):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(2, 10)
        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(155, 130, 95)
        )

    return img

def draw_manuscript(script, index, output_dir):
    font_path = find_font(script)

    image = create_background()

    draw = ImageDraw.Draw(image)

    font_size = random.randint(42, 58)
    font = ImageFont.truetype(str(font_path), font_size)

    lines = []

    for _ in range(random.randint(8, 14)):
        lines.append(
            random.choice(SCRIPTS[script]["text"])
        )

    x = random.randint(100, 180)
    y = random.randint(120, 200)

    annotation_lines = []

    for line_number, text in enumerate(lines, start=1):

        draw.text(
            (x, y),
            text,
            font=font,
            fill=(55, 40, 30)
        )

        if random.random() < 0.18:
            draw.line(
                (x, y + font_size + 5,
                 x + random.randint(100, 300),
                 y + font_size + 5),
                fill=(130, 40, 30),
                width=3
            )

        if random.random() < 0.12:
            draw.ellipse(
                (
                    x - 20,
                    y + 10,
                    x - 5,
                    y + 25
                ),
                outline=(150, 30, 30),
                width=3
            )

        annotation_lines.append(
            f"- line {line_number}: {text}"
        )

        y += random.randint(90, 125)

        if y > 1750:
            break

    image = image.filter(ImageFilter.GaussianBlur(0.15))

    png_path = output_dir / f"{script}_{index:03d}.png"
    md_path = output_dir / f"{script}_{index:03d}.md"

    image.save(png_path)

    markdown = f"""# Synthetic Manuscript

## Script
{script}

## Sample ID
{index}

## Annotations

{chr(10).join(annotation_lines)}
"""

    md_path.write_text(
        markdown,
        encoding="utf-8"
    )

    return png_path, md_path


def generate_dataset(count=100):

    splits = {
        "train": int(count * 0.85),
        "validation": int(count * 0.10),
        "test": count - int(count * 0.85) - int(count * 0.10)
    }

    print("=" * 70)
    print("SYNTHETIC MANUSCRIPT GENERATOR")
    print("=" * 70)

    for script in SCRIPTS:

        print()
        print(f"[{script}]")

        font = find_font(script)
        print(f"Font: {font}")

        number = 1

        for split, amount in splits.items():

            split_dir = OUTPUT / script / split
            split_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            print(
                f"Generating {amount} images "
                f"for {split}..."
            )

            for _ in range(amount):

                draw_manuscript(
                    script,
                    number,
                    split_dir
                )

                number += 1

        print(
            f"Completed {script}: "
            f"{count} images"
        )

    print()
    print("=" * 70)
    print("DATASET GENERATION COMPLETE")
    print("=" * 70)
    print(f"Output: {OUTPUT}")


def generate_preview():

    preview_dir = ROOT / "output" / "preview"
    preview_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 70)
    print("GENERATING PREVIEWS")
    print("=" * 70)

    for script in SCRIPTS:

        print(f"\n[{script}]")

        font = find_font(script)
        print(f"Font: {font}")

        draw_manuscript(
            script,
            1,
            preview_dir
        )

    print()
    print("Preview generation complete.")
    print(f"Preview folder: {preview_dir}")


def create_zip():

    zip_path = ROOT / "output" / "synthetic_manuscript_dataset.zip"

    dataset_root = OUTPUT

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as z:

        for file in dataset_root.rglob("*"):

            if file.is_file():

                z.write(
                    file,
                    file.relative_to(
                        dataset_root
                    )
                )

    print(f"ZIP created: {zip_path}")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--preview",
        action="store_true"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=100
    )

    parser.add_argument(
        "--zip",
        action="store_true"
    )

    args = parser.parse_args()

    if args.preview:

        generate_preview()

    else:

        generate_dataset(args.count)

        if args.zip:
            create_zip()


if __name__ == "__main__":
    main()
