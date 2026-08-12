"""有道网页版词典接口（dict.youdao.com/jsonapi），补充多词性释义与音标。

官方 openapi 已不返回 basic/web 词典字段（见 CLAUDE.md 实测记录），
故用该免费接口取词典数据；无签名，失败时静默降级为纯翻译。
"""
import json
import urllib.parse
import urllib.request

API_URL = "https://dict.youdao.com/jsonapi?q="

# 与 youdao.py 相同原因：国内服务直连，绕过系统代理
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def lookup(q, timeout=5):
    """查询词典，返回解析结果；任何异常返回空结果。"""
    try:
        with _OPENER.open(API_URL + urllib.parse.quote(q), timeout=timeout) as resp:
            return parse_jsonapi(json.loads(resp.read().decode("utf-8")))
    except Exception:
        return parse_jsonapi({})


def _first_word(data, key):
    words = (data.get(key) or {}).get("word") or []
    return words[0] if words else {}


def _iter_tr_l(word):
    for trs in word.get("trs") or []:
        tr = trs.get("tr") or []
        if tr:
            yield (tr[0].get("l") or {})


def parse_jsonapi(data):
    """英文词取 ec（多词性释义），中文词取 ce（词条 — 解释）。"""
    result = {"phonetic_us": None, "phonetic_uk": None, "defs": []}

    ec_word = _first_word(data, "ec")
    if ec_word:
        result["phonetic_us"] = ec_word.get("usphone") or None
        result["phonetic_uk"] = ec_word.get("ukphone") or None
        for l in _iter_tr_l(ec_word):
            i = l.get("i") or []
            if i and isinstance(i[0], str) and i[0]:
                result["defs"].append(i[0])
        return result

    ce_word = _first_word(data, "ce")
    for l in _iter_tr_l(ce_word):
        words = [
            seg.get("#text", "") if isinstance(seg, dict) else seg
            for seg in l.get("i") or []
        ]
        text = "".join(words).strip()
        tran = (l.get("#tran") or "").strip()
        if text and tran:
            result["defs"].append(text + " — " + tran)
        elif text:
            result["defs"].append(text)
    return result
