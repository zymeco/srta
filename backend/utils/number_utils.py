# 숫자 포맷팅 유틸리티

def round1(v):
    try:
        return round(float(v), 1)
    except Exception:
        return 0.0


def round2(v):
    try:
        return round(float(v), 2)
    except Exception:
        return 0.0


def safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default


def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def clamp(v, lo, hi):
    try:
        return max(lo, min(hi, v))
    except Exception:
        return lo


def format_won(v):
    try:
        v = int(v)
        if v >= 1_0000_0000_0000:
            return f"{v/1_0000_0000_0000:.2f}조"
        if v >= 1_0000_0000:
            return f"{v/1_0000_0000:.1f}억"
        return f"{v:,}"
    except Exception:
        return "-"
