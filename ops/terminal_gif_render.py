"""Shared terminalizer-style GIF renderer for landing demos."""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pip install pillow") from exc

# Theme aligned with ops/terminalizer.yml + landing globals.css
BG = (10, 10, 10)
FG = (176, 176, 176)
MINT = (60, 255, 208)
DIM = (120, 130, 125)
BORDER = (60, 255, 208)
TITLE_BG = (28, 28, 30)
DOT_RED = (255, 95, 87)
DOT_YELLOW = (255, 189, 46)
DOT_GREEN = (40, 200, 64)

WIDTH, HEIGHT = 920, 520
PAD = 28
TITLE_H = 44
FONT_SIZE = 15
LINE_H = 22
CURSOR_BLINK = 6

ScriptLine = tuple[str, str, int]


def font(size: int = FONT_SIZE) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Users\acuba\AppData\Local\Microsoft\Windows\Fonts\JetBrainsMono-Regular.ttf"),
        Path("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"),
        Path("/System/Library/Fonts/Supplemental/Andale Mono.ttf"),
        Path("C:/Windows/Fonts/consola.ttf"),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def draw_frame(
    visible: list[tuple[str, str]],
    cursor_on: bool,
    tick: int,
    *,
    title: str,
) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    fnt = font()

    draw.rounded_rectangle((12, 12, WIDTH - 12, HEIGHT - 12), radius=14, outline=BORDER, width=2)
    draw.rounded_rectangle((14, 14, WIDTH - 14, HEIGHT - 14), radius=12, outline=(30, 90, 75), width=1)

    draw.rounded_rectangle((PAD, PAD, WIDTH - PAD, PAD + TITLE_H), radius=10, fill=TITLE_BG)
    draw.rectangle((PAD + 8, PAD + TITLE_H - 2, WIDTH - PAD - 8, PAD + TITLE_H), fill=TITLE_BG)
    for i, color in enumerate((DOT_RED, DOT_YELLOW, DOT_GREEN)):
        x = PAD + 16 + i * 18
        draw.ellipse((x, PAD + 16, x + 10, PAD + 26), fill=color)
    draw.text((PAD + 72, PAD + 12), title[:52], font=fnt, fill=MINT)

    y = PAD + TITLE_H + 18
    x0 = PAD + 16
    max_y = HEIGHT - PAD - 12

    for kind, text in visible:
        if y > max_y:
            break
        if kind == "prompt":
            draw.text((x0, y), "$ ", font=fnt, fill=MINT)
            draw.text((x0 + draw.textlength("$ ", font=fnt), y), text, font=fnt, fill=MINT)
        elif kind == "head":
            draw.text((x0, y), text, font=fnt, fill=MINT)
        elif kind == "dim":
            draw.text((x0, y), text, font=fnt, fill=DIM)
        else:
            draw.text((x0 + 8, y), text, font=fnt, fill=FG)
        y += LINE_H

    if cursor_on and y <= max_y:
        cx = x0
        if visible and visible[-1][0] == "prompt":
            cx = x0 + draw.textlength("$ " + visible[-1][1], font=fnt)
        elif visible and visible[-1][0] in ("out", "head", "dim"):
            cx = x0 + 8 + draw.textlength(visible[-1][1], font=fnt)
        if tick % CURSOR_BLINK < CURSOR_BLINK // 2:
            draw.rectangle((cx, y - 2, cx + 9, y + FONT_SIZE), fill=MINT)

    return img


def build_frames(script: list[ScriptLine], *, title: str) -> list[Image.Image]:
    frames: list[Image.Image] = []
    visible: list[tuple[str, str]] = []
    tick = 0

    for kind, text, hold in script:
        if kind == "prompt":
            for n in range(1, len(text) + 1):
                partial = ("prompt", text[:n])
                if visible and visible[-1][0] == "prompt":
                    visible[-1] = partial
                else:
                    visible.append(partial)
                for _ in range(2):
                    frames.append(draw_frame(visible, cursor_on=True, tick=tick, title=title))
                    tick += 1
            for _ in range(hold):
                frames.append(draw_frame(visible, cursor_on=False, tick=tick, title=title))
                tick += 1
        else:
            visible.append((kind, text))
            for _ in range(hold):
                frames.append(draw_frame(visible, cursor_on=False, tick=tick, title=title))
                tick += 1

    for _ in range(14):
        frames.append(draw_frame(visible, cursor_on=False, tick=tick, title=title))
        tick += 1
    return frames


def write_gif(frames: list[Image.Image], out: Path, *, duration_ms: int = 72) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)

    def quantize(im: Image.Image) -> Image.Image:
        return im.convert("P", palette=Image.Palette.ADAPTIVE, colors=48)

    first, *rest = frames
    quantize(first).save(
        out,
        save_all=True,
        append_images=[quantize(f) for f in rest],
        duration=duration_ms,
        loop=0,
        optimize=True,
        disposal=2,
    )
