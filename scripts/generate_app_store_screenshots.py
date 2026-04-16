#!/usr/bin/env python3
"""Generate App Store screenshots from real raw app screenshots and a JSON config."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont


DEFAULT_FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
SYSTEM_FONT = "/System/Library/Fonts/STHeiti Light.ttc"
SYSTEM_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"


SAMPLE_CONFIG = {
    "output_root": "AppStoreAssets/screenshots",
    "overview": True,
    "sets": [
        {
            "id": "iphone",
            "size": [1284, 2778],
            "canvas_size": [1320, 2868],
            "device_width": 880,
            "device_position": [220, 880],
            "raw_root": "AppStoreAssets/raw/iphone",
            "languages": {
                "en": {"raw": "AppStoreAssets/raw/iphone/en/01.png"},
                "zh-Hans": {"raw": "AppStoreAssets/raw/iphone/zh-Hans/01.png"},
            },
            "themes": [
                {
                    "filename": "01_core_promise.png",
                    "eyebrow": {"en": "Core Feature", "zh-Hans": "核心功能"},
                    "headline": {"en": "Real app UI\nwith real value", "zh-Hans": "真实界面\n表达真实卖点"},
                    "subtitle": {"en": "Use raw simulator screenshots, then add marketing copy outside the app UI.", "zh-Hans": "使用模拟器真实截图，并在 App UI 外层添加营销文案。"},
                    "pills": {"en": ["Real UI", "Localized", "Sized"], "zh-Hans": ["真实界面", "本地化", "尺寸正确"]},
                    "accent": "#097747",
                }
            ],
        }
    ],
}


def hex_color(value: str | list[int] | tuple[int, int, int], fallback=(9, 119, 71)) -> tuple[int, int, int]:
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        return int(value[0]), int(value[1]), int(value[2])
    if isinstance(value, str):
        value = value.strip().lstrip("#")
        if len(value) == 6:
            return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    return fallback


def get_text(value: Any, lang: str, default: str = "") -> str:
    if isinstance(value, dict):
        return value.get(lang) or value.get(lang.split("-")[0]) or value.get("en") or next(iter(value.values()), default)
    if isinstance(value, list):
        return ", ".join(map(str, value))
    if value is None:
        return default
    return str(value)


def get_list(value: Any, lang: str) -> list[str]:
    selected = value
    if isinstance(value, dict):
        selected = value.get(lang) or value.get(lang.split("-")[0]) or value.get("en") or []
    if isinstance(selected, list):
        return [str(v) for v in selected]
    if isinstance(selected, str) and selected:
        return [selected]
    return []


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in ([SYSTEM_BOLD, SYSTEM_FONT, DEFAULT_FONT] if bold else [SYSTEM_FONT, DEFAULT_FONT]):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def linear_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, top)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = color
    return img.convert("RGBA")


def add_map_lines(draw: ImageDraw.ImageDraw, size: tuple[int, int], accent: tuple[int, int, int]) -> None:
    w, h = size
    for base in range(-200, h, 210):
        points = []
        for x in range(-80, w + 120, 24):
            y = base + 42 * math.sin((x + base) / 120) + 18 * math.sin(x / 43)
            points.append((x, y))
        draw.line(points, fill=(*accent, 20), width=3)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: list[str] = []
    for source in text.splitlines():
        if not source:
            lines.append("")
            continue
        if " " in source:
            line = ""
            for word in source.split(" "):
                candidate = word if not line else f"{line} {word}"
                if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
                    line = candidate
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        else:
            line = ""
            for char in source:
                candidate = line + char
                if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
                    line = candidate
                else:
                    if line:
                        lines.append(line)
                    line = char
            if line:
                lines.append(line)
    return "\n".join(lines)


def draw_pill(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int], size=32) -> int:
    x, y = xy
    fnt = font(size, True)
    bbox = draw.textbbox((0, 0), text, font=fnt)
    width = bbox[2] - bbox[0] + 52
    height = size + 36
    draw.rounded_rectangle((x, y, x + width, y + height), radius=height // 2, fill=fill)
    draw.text((x + 26, y + 14), text, font=fnt, fill=(255, 255, 255))
    return width


def rounded_paste(base: Image.Image, img: Image.Image, xy: tuple[int, int], radius: int) -> None:
    x, y = xy
    shadow = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((40, 40, 40 + img.width, 40 + img.height), radius=radius, fill=(5, 30, 22, 52))
    shadow = shadow.filter(ImageFilter.GaussianBlur(26))
    base.alpha_composite(shadow, (x - 40, y - 26))
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, img.width, img.height), radius=radius, fill=255)
    base.paste(img.convert("RGBA"), xy, mask)


def resize_width(img: Image.Image, width: int) -> Image.Image:
    height = round(img.height * width / img.width)
    return img.resize((width, height), Image.Resampling.LANCZOS)


def crop_raw(raw: Image.Image, theme: dict) -> Image.Image:
    crop = theme.get("crop")
    if crop and len(crop) == 4:
        return raw.crop(tuple(map(int, crop)))
    top = theme.get("crop_top")
    height = theme.get("crop_height")
    if top is not None and height is not None:
        top = int(top)
        return raw.crop((0, top, raw.width, min(raw.height, top + int(height))))
    return raw


def make_canvas(canvas_size: tuple[int, int], accent: tuple[int, int, int]) -> Image.Image:
    bg = linear_gradient(canvas_size, (244, 250, 247), (224, 242, 247))
    overlay = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    add_map_lines(od, canvas_size, accent)
    od.rectangle((0, 0, canvas_size[0], 520), fill=(255, 255, 255, 44))
    bg.alpha_composite(overlay)
    return bg


def render_theme(config_set: dict, lang: str, lang_cfg: dict, theme: dict, out_dir: Path) -> Path:
    target_size = tuple(config_set.get("size", [1284, 2778]))
    canvas_size = tuple(config_set.get("canvas_size", target_size))
    accent = hex_color(theme.get("accent", config_set.get("accent", "#097747")))
    raw_path = Path(theme.get("raw") or lang_cfg.get("raw"))
    raw = Image.open(raw_path).convert("RGB")
    canvas = make_canvas(canvas_size, accent)
    draw = ImageDraw.Draw(canvas)

    margin_x = int(config_set.get("margin_x", 96))
    eyebrow_y = int(config_set.get("eyebrow_y", 100))
    title_y = int(config_set.get("title_y", 220))
    subtitle_y = int(config_set.get("subtitle_y", 430))
    pill_y = int(config_set.get("pill_y", 640))

    eyebrow = get_text(theme.get("eyebrow"), lang)
    headline = get_text(theme.get("headline"), lang)
    subtitle = get_text(theme.get("subtitle"), lang)
    if eyebrow:
        draw_pill(draw, (margin_x, eyebrow_y), eyebrow, accent, int(config_set.get("eyebrow_size", 30)))
    title_font = font(int(theme.get("headline_size", config_set.get("headline_size", 82))), True)
    draw.multiline_text((margin_x, title_y), headline, font=title_font, fill=(12, 31, 26), spacing=8)
    subtitle_font = font(int(theme.get("subtitle_size", config_set.get("subtitle_size", 38))))
    draw.multiline_text(
        (margin_x, subtitle_y),
        wrap_text(draw, subtitle, subtitle_font, canvas_size[0] - margin_x * 2),
        font=subtitle_font,
        fill=(58, 77, 73),
        spacing=10,
    )

    px = margin_x
    pill_colors = [hex_color(c) for c in theme.get("pill_colors", ["#097747", "#0A84FF", "#E6654B"])]
    for i, label in enumerate(get_list(theme.get("pills"), lang)):
        px += draw_pill(draw, (px, pill_y), label, pill_colors[i % len(pill_colors)], int(config_set.get("pill_size", 30))) + 22

    device_width = int(theme.get("device_width", config_set.get("device_width", 900)))
    device_position = theme.get("device_position", config_set.get("device_position", [margin_x, 780]))
    device_radius = int(theme.get("device_radius", config_set.get("device_radius", 58)))
    screenshot = resize_width(crop_raw(raw, theme), device_width)
    rounded_paste(canvas, screenshot, tuple(map(int, device_position)), device_radius)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_name = theme.get("filename") or f"{theme.get('id', 'screenshot')}.png"
    out_path = out_dir / out_name
    canvas.convert("RGB").resize(target_size, Image.Resampling.LANCZOS).save(out_path, quality=96)
    return out_path


def make_overview(out_dir: Path, image_paths: list[Path], name: str) -> None:
    if not image_paths:
        return
    images = [Image.open(p).convert("RGB") for p in image_paths]
    thumb_w = 300
    gap = 28
    thumb_h = round(thumb_w * images[0].height / images[0].width)
    cols = min(3, len(images))
    rows = math.ceil(len(images) / cols)
    overview = Image.new("RGB", (thumb_w * cols + gap * (cols + 1), thumb_h * rows + gap * (rows + 1)), (235, 242, 239))
    for i, img in enumerate(images):
        thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = gap + (i % cols) * (thumb_w + gap)
        y = gap + (i // cols) * (thumb_h + gap)
        overview.paste(thumb, (x, y))
    overview.save(out_dir / name, quality=96)


def generate(config: dict) -> None:
    output_root = Path(config.get("output_root", "AppStoreAssets/screenshots"))
    for config_set in config.get("sets", []):
        set_id = config_set.get("id", "set")
        for lang, lang_cfg in config_set.get("languages", {}).items():
            out_dir = output_root / set_id / lang
            paths = [render_theme(config_set, lang, lang_cfg, theme, out_dir) for theme in config_set.get("themes", [])]
            if config.get("overview", True):
                make_overview(output_root / set_id, paths, f"{lang}_overview.png")
            print(f"Wrote {len(paths)} screenshots to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Screenshot JSON config")
    parser.add_argument("--write-sample-config", help="Write a sample config and exit")
    args = parser.parse_args()

    if args.write_sample_config:
        Path(args.write_sample_config).write_text(json.dumps(SAMPLE_CONFIG, ensure_ascii=False, indent=2) + "\n")
        return
    if not args.config:
        raise SystemExit("Provide --config or --write-sample-config")
    generate(json.loads(Path(args.config).read_text()))


if __name__ == "__main__":
    main()
