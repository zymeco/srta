# 안전 계산 유틸. 0 나눗셈/None/예외에서도 죽지 않도록.

def safe_div(a, b, default=0.0):
    try:
        if b is None or b == 0:
            return default
        return a / b
    except Exception:
        return default


def safe_pct(a, b, default=0.0):
    try:
        if b is None or b == 0:
            return default
        return (a - b) / b * 100.0
    except Exception:
        return default


def safe_mean(values):
    try:
        nums = [v for v in values if v is not None]
        if not nums:
            return 0.0
        return sum(nums) / len(nums)
    except Exception:
        return 0.0


def safe_last(values, default=0):
    try:
        if not values:
            return default
        return values[-1]
    except Exception:
        return default
