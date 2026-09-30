"""Render the static toolkit map used in the profile README."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "toolkit.png"
SIZE = (1000, 372)


def font(size: int, bold: bool = False):
    choices = (
        ["C:/Windows/Fonts/seguisb.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for name in choices:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


image = Image.new("RGB", SIZE, (8, 18, 33))
draw = ImageDraw.Draw(image)
cards = [
    (30, 24, "01", "MODELING", "PyTorch  ·  Transformers  ·  Hugging Face",
     "scikit-learn  ·  OpenCV  ·  NumPy", (118, 242, 213)),
    (510, 24, "02", "DATA", "pandas  ·  SQL  ·  PostgreSQL",
     "MySQL  ·  MongoDB  ·  Jupyter", (118, 196, 255)),
    (30, 193, "03", "INTERFACES", "FastAPI  ·  Flask  ·  Streamlit",
     "JavaScript  ·  VS Code Extension API", (255, 188, 144)),
    (510, 193, "04", "DELIVERY", "Docker  ·  Kubernetes  ·  MLflow",
     "Redis  ·  Git", (181, 159, 255)),
]
for x, y, number, label, row1, row2, color in cards:
    draw.rounded_rectangle((x, y, x + 460, y + 151), radius=18,
                           fill=(13, 36, 53), outline=(42, 78, 94), width=2)
    draw.rounded_rectangle((x + 22, y + 22, x + 58, y + 27), radius=2, fill=color)
    draw.text((x + 22, y + 40), label, font=font(26, True), fill=(242, 248, 251))
    draw.text((x + 402, y + 23), number, font=font(19, True), fill=color)
    draw.text((x + 22, y + 88), row1, font=font(20), fill=(184, 210, 219))
    draw.text((x + 22, y + 116), row2, font=font(20), fill=(184, 210, 219))
image.save(OUT, optimize=True)
