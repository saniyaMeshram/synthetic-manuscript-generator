from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

tests = [
    ("devanagari", "श्रीरामचन्द्र कृपालु भज मन", "fonts/devanagari.ttf"),
    ("modi", "𑘦𑘰𑘥𑘳𑘭𑘿𑘨𑘱", "fonts/modi.ttf"),
    ("sharada", "𑆯𑆳𑆫𑆢𑆳", "fonts/sharada.ttf"),
]

for name, text, font_path in tests:
    image = Image.new("RGB", (1200, 250), "white")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font_path, 60)

    draw.text(
        (40, 80),
        text,
        font=font,
        fill="black",
    )

    output_file = output_dir / f"{name}_font_test.png"
    image.save(output_file)

    print(f"{name}: OK -> {output_file}")

print("ALL FONT TESTS CREATED")