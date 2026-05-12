# PWA용 PNG 아이콘 자동 생성 스크립트
# 사용법:
#   python tools/generate_icons.py
# 출력:
#   frontend/public/icons/icon-192.png
#   frontend/public/icons/icon-512.png
#   frontend/public/icons/icon-512-maskable.png
#   frontend/public/icons/apple-touch-icon.png (180x180)
#   frontend/public/icons/favicon.png (32x32)

import os
import math
from PIL import Image, ImageDraw, ImageFilter

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "icons")
os.makedirs(OUT_DIR, exist_ok=True)


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def gradient_bg(size, c1, c2):
    """대각선 그라데이션 배경."""
    img = Image.new("RGB", (size, size), c1)
    px = img.load()
    diag = math.sqrt(2) * size
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            px[x, y] = lerp(c1, c2, t)
    return img


def round_corners(img, radius):
    """Mask 라운드 모서리."""
    size = img.size[0]
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size, size], radius=radius, fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def make_icon(size: int, *, maskable: bool = False, with_text: bool = True):
    """SRTA 로고 아이콘 생성."""
    # 배경 그라데이션 (보라 → 핑크)
    bg = gradient_bg(size, (129, 140, 248), (244, 114, 182))  # indigo-400 → pink-400

    img = bg.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # maskable은 safe zone 80% 이내에 콘텐츠 위치
    if maskable:
        # 배경은 풀브리드(전체 채우기), 콘텐츠는 80% 안쪽
        pass

    # 상승 차트 라인
    margin = int(size * 0.18)
    chart_w = size - margin * 2
    chart_h = int(size * 0.32)
    chart_y = int(size * 0.40)
    pts_norm = [
        (0.00, 0.78),
        (0.20, 0.50),
        (0.36, 0.62),
        (0.55, 0.30),
        (0.72, 0.40),
        (1.00, 0.10),
    ]
    pts = [
        (margin + int(chart_w * x), chart_y + int(chart_h * y))
        for (x, y) in pts_norm
    ]
    line_w = max(4, int(size * 0.035))
    draw.line(pts, fill=(255, 255, 255, 255), width=line_w, joint="curve")
    # 종점 강조 점
    r = max(5, int(size * 0.045))
    cx, cy = pts[-1]
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))

    # 텍스트 SRTA
    if with_text and not maskable:
        try:
            from PIL import ImageFont
            font_size = int(size * 0.18)
            font = None
            for name in ("arialbd.ttf", "Arial Bold.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
                try:
                    font = ImageFont.truetype(name, font_size)
                    break
                except Exception:
                    continue
            if font:
                txt = "SRTA"
                bbox = draw.textbbox((0, 0), txt, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                tx = (size - tw) // 2
                ty = int(size * 0.74) - th // 2
                draw.text((tx, ty), txt, fill=(255, 255, 255, 240), font=font)
        except Exception:
            pass

    # 라운드 모서리 (maskable 아닐 때만)
    if not maskable:
        img = round_corners(img, int(size * 0.22))

    return img


def main():
    print("[icons] 생성 중...")

    # 표준 (라운드 모서리)
    make_icon(192).save(os.path.join(OUT_DIR, "icon-192.png"), "PNG")
    make_icon(512).save(os.path.join(OUT_DIR, "icon-512.png"), "PNG")
    print("  icon-192.png / icon-512.png")

    # Maskable (배경 풀, 라운드 없음)
    make_icon(512, maskable=True).save(os.path.join(OUT_DIR, "icon-512-maskable.png"), "PNG")
    make_icon(192, maskable=True).save(os.path.join(OUT_DIR, "icon-192-maskable.png"), "PNG")
    print("  icon-512-maskable.png / icon-192-maskable.png")

    # Apple touch icon (라운드 없이, iOS가 알아서 처리)
    img180 = make_icon(180, maskable=True)
    img180.save(os.path.join(OUT_DIR, "apple-touch-icon.png"), "PNG")
    print("  apple-touch-icon.png")

    # Favicon
    make_icon(32, with_text=False).save(os.path.join(OUT_DIR, "favicon.png"), "PNG")
    print("  favicon.png")

    print(f"[icons] 완료: {os.path.abspath(OUT_DIR)}")


if __name__ == "__main__":
    main()
