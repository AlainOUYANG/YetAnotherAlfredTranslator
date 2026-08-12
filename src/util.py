"""语言检测、拆词、结果缓存。仅用标准库。"""
import hashlib
import json
import os
import re
import time

# CJK 统一表意文字 / 扩展 A / 兼容表意文字
_CJK_RE = re.compile(r"[一-鿿㐀-䶿豈-﫿]")

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def has_cjk(s):
    return bool(_CJK_RE.search(s))


def detect_direction(q):
    """返回 (from, to)：含任意 CJK 字符 → 中译英，否则 auto → 中文。"""
    if has_cjk(q):
        return ("zh-CHS", "en")
    return ("auto", "zh-CHS")


def split_token(q):
    """驼峰/下划线拆词。仅对无空格单 token 生效，保留连续大写缩略词。"""
    if " " in q or has_cjk(q):
        return q
    s = q.replace("_", " ")
    s = _CAMEL_RE.sub(" ", s)
    return re.sub(r" +", " ", s).strip()


def _cache_path(cache_dir, q, direction):
    key = hashlib.md5((q + "|" + direction).encode("utf-8")).hexdigest()
    return os.path.join(cache_dir, key + ".json")


def cache_get(cache_dir, q, direction, ttl=86400):
    path = _cache_path(cache_dir, q, direction)
    try:
        if time.time() - os.path.getmtime(path) > ttl:
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def cache_set(cache_dir, q, direction, data):
    try:
        os.makedirs(cache_dir, exist_ok=True)
        with open(_cache_path(cache_dir, q, direction), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass  # 缓存失败不影响主流程
