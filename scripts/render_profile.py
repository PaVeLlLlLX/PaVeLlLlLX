"""Render lightweight animated artwork for the GitHub profile README.

Requires Pillow: python -m pip install Pillow
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH = 1000
HERO_HEIGHT = 320
FOOTER_HEIGHT = 176
FRAMES = 28
DURATION_MS = 120

BG_TOP = (8, 18, 33)
BG_BOTTOM = (13, 34, 51)
MINT = (118, 242, 213)
BLUE = (118, 196, 255)
PEACH = (255, 188, 144)
LILAC = (181, 159, 255)
WHITE = (242, 248, 251)
MUTED = (159, 188, 205)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = (
        ["C:/Windows/Fonts/seguisb.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def background(height: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        blend = y / max(height - 1, 1)
        color = tuple(round(a * (1 - blend) + b * blend) for a, b in zip(BG_TOP, BG_BOTTOM))
        draw.line((0, y, WIDTH, y), fill=color)
    for x in range(0, WIDTH, 50):
        draw.line((x, 0, x, height), fill=(18, 43, 57), width=1)
    for y in range(0, height, 50):
        draw.line((0, y, WIDTH, y), fill=(18, 43, 57), width=1)
    return image


def particles(seed: int, left: int, height: int, count: int) -> list[tuple[float, float, float, float, int]]:
    randomizer = random.Random(seed)
    return [
        (
            randomizer.uniform(left, WIDTH - 34),
            randomizer.uniform(25, height - 25),
            randomizer.uniform(1.2, 3.5),
            randomizer.uniform(0, math.tau),
            randomizer.randrange(4),
        )
        for _ in range(count)
    ]


def draw_particles(draw: ImageDraw.ImageDraw, points: list, phase: float, height: int) -> None:
    colors = [MINT, BLUE, PEACH, LILAC]
    moving = []
    for x, y, radius, offset, index in points:
        px = x + math.sin(phase + offset) * 11
        py = y + math.cos(phase * .75 + offset) * 8
        moving.append((px, py, radius, colors[index]))
    for index, (x, y, _, _) in enumerate(moving[:18]):
        for x2, y2, _, _ in moving[index + 1:18]:
            if (x - x2) ** 2 + (y - y2) ** 2 < 115 ** 2:
                draw.line((x, y, x2, y2), fill=(32, 76, 92), width=1)
    for x, y, radius, color in moving:
        r = radius
        draw.ellipse((x - r * 2.6, y - r * 2.6, x + r * 2.6, y + r * 2.6), fill=(21, 68, 80))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


def hero_frame(index: int, base: Image.Image, points: list) -> Image.Image:
    image = base.copy()
    draw = ImageDraw.Draw(image)
    phase = math.tau * index / FRAMES
    draw.rounded_rectangle((18, 18, WIDTH - 18, HERO_HEIGHT - 18), radius=22, outline=(42, 78, 94), width=2)
    draw.ellipse((689, 26, 969, 306), outline=(37, 88, 104), width=2)
    draw.ellipse((731, 68, 927, 264), outline=(36, 106, 113), width=2)
    draw.ellipse((777, 114, 881, 218), outline=(39, 124, 127), width=1)
    draw_particles(draw, points, phase, HERO_HEIGHT)
    orbit_x = 829 + math.cos(phase) * 98
    orbit_y = 166 + math.sin(phase) * 98
    draw.ellipse((orbit_x - 5, orbit_y - 5, orbit_x + 5, orbit_y + 5), fill=PEACH)
    draw.line((55, 67, 107, 67), fill=MINT, width=4)
    draw.text((55, 43), "HELLO, I'M", font=font(17, True), fill=MUTED, stroke_width=0)
    draw.text((50, 108), "PAVEL IVANKOV", font=font(60, True), fill=WHITE)
    draw.text((55, 194), "DATA SCIENCE  /  ML SYSTEMS  /  SIDE PROJECTS", font=font(21, True), fill=MINT)
    draw.line((55, 260, 525, 260), fill=(65, 122, 137), width=2)
    draw.text((55, 270), "FROM MESSY INPUTS TO USEFUL THINGS", font=font(15), fill=MUTED)
    return image


def footer_frame(index: int, base: Image.Image, points: list) -> Image.Image:
    image = base.copy()
    draw = ImageDraw.Draw(image)
    phase = math.tau * index / FRAMES
    draw.rounded_rectangle((18, 17, WIDTH - 18, FOOTER_HEIGHT - 17), radius=20, outline=(42, 78, 94), width=2)
    draw_particles(draw, points, phase + 1.2, FOOTER_HEIGHT)
    for line_index in range(3):
        coords = []
        for x in range(430, 953, 9):
            y = 90 + (line_index - 1) * 19 + math.sin(x / 52 + phase + line_index) * 13
            coords.append((x, y))
        draw.line(coords, fill=[(35, 102, 111), (48, 125, 132), (42, 89, 126)][line_index], width=2)
    draw.text((53, 49), "ALWAYS EXPERIMENTING", font=font(30, True), fill=WHITE)
    draw.text((55, 101), "DATA  →  MODELS  →  SOMETHING USEFUL", font=font(17), fill=MINT)
    return image


def save_animation(name: str, images: list[Image.Image]) -> None:
    images[0].save(ASSETS / f"{name}.png", optimize=True)
    palette_frames = [
        frame.quantize(colors=96, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        for frame in images
    ]
    palette_frames[0].save(
        ASSETS / f"{name}.gif",
        save_all=True,
        append_images=palette_frames[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    hero_base = background(HERO_HEIGHT)
    footer_base = background(FOOTER_HEIGHT)
    hero_points = particles(2026, 655, HERO_HEIGHT, 42)
    footer_points = particles(2718, 430, FOOTER_HEIGHT, 34)
    save_animation("hero", [hero_frame(i, hero_base, hero_points) for i in range(FRAMES)])
    save_animation("signal", [footer_frame(i, footer_base, footer_points) for i in range(FRAMES)])


if __name__ == "__main__":
    main()
