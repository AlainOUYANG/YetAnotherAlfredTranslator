"""Script Filter 入口：读配置 → 并行调有道翻译与词典 → 输出 Alfred JSON。"""
import json
import os
import sys
import urllib.error
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import dictapi
import util
import youdao

BUNDLE_ID = "com.ouyang.yat"
REGISTER_URL = "https://ai.youdao.com/"
CONFIG_URL = (
    "alfredpreferences://navigateto/workflows>workflow>" + BUNDLE_ID + ">userconfig"
)

ICON_TRANSLATE = "icons/translate.png"
# 超过该长度视为句子，不再查词典释义
DICT_LOOKUP_MAX_CHARS = 20


def output(items):
    print(json.dumps({"items": items}, ensure_ascii=False))


def error_item(title, subtitle=""):
    return {
        "title": title,
        "subtitle": subtitle,
        "valid": False,
        "icon": {"path": ICON_TRANSLATE},
    }


def guide_items():
    return [
        {
            "title": "未配置有道智云密钥",
            "subtitle": "回车打开有道智云官网，注册应用获取应用 ID 和密钥（免费）",
            "arg": REGISTER_URL,
            "icon": {"path": ICON_TRANSLATE},
            "variables": {"action": "open_url", "url": REGISTER_URL},
        },
        {
            "title": "打开本 Workflow 配置面板",
            "subtitle": "回车打开 Alfred 配置面板，填入应用 ID 和密钥",
            "arg": CONFIG_URL,
            "icon": {"path": ICON_TRANSLATE},
            "variables": {"action": "open_url", "url": CONFIG_URL},
        },
    ]


def _speak_mods(en_text, speak_url):
    """⌘ 本地发音 / ⌥ 在线发音，读英文侧文本。"""
    return {
        "cmd": {
            "subtitle": "🔊 本地发音: " + en_text,
            "arg": en_text,
            "variables": {"action": "speak_local", "speak_lang": "en"},
        },
        "alt": {
            "subtitle": "📣 在线发音: " + en_text,
            "arg": en_text,
            "variables": {"action": "speak_online", "speak_url": speak_url or ""},
        },
    }


def build_items(parsed, q, direction, dict_info=None):
    """由翻译响应与词典结果组装 Alfred items。q 为实际送翻的文本。"""
    dict_info = dict_info or {"phonetic_us": None, "phonetic_uk": None, "defs": []}
    translation = parsed["translation"]
    if not translation:
        return [error_item("未返回翻译结果", "原文: " + q)]

    en_text = translation if direction[0] == "zh-CHS" else q
    speak_url = parsed["speech_us"] or parsed["speech_uk"] or parsed["t_speak_url"]
    mods = _speak_mods(en_text, speak_url)
    icon = {"path": ICON_TRANSLATE}

    phonetic_us = parsed["phonetic_us"] or dict_info["phonetic_us"]
    phonetic_uk = parsed["phonetic_uk"] or dict_info["phonetic_uk"]
    phonetics = []
    if phonetic_us:
        phonetics.append("[美: {}]".format(phonetic_us))
    if phonetic_uk:
        phonetics.append("[英: {}]".format(phonetic_uk))
    if not phonetics and parsed["phonetic"]:
        phonetics.append("[{}]".format(parsed["phonetic"]))
    subtitle = q + ("  " + " ".join(phonetics) if phonetics else "")

    quicklook = "https://www.youdao.com/result?word={}&lang=en".format(
        urllib.parse.quote(en_text)
    )

    def item(title, sub, arg):
        return {
            "title": title,
            "subtitle": sub,
            "arg": arg,
            "quicklookurl": quicklook,
            "icon": icon,
            "text": {"copy": arg, "largetype": title},
            "mods": mods,
        }

    items = [item(translation, subtitle, translation)]
    # 多词性释义：openapi 的 explains（如恢复返回）优先，其后补 jsonapi 的释义并去重
    seen = {translation}
    for exp in parsed["explains"] + dict_info["defs"]:
        if exp in seen:
            continue
        seen.add(exp)
        items.append(item(exp, subtitle, exp))
    if parsed["wfs"]:
        wfs_text = "  ".join("{}: {}".format(n, v) for n, v in parsed["wfs"])
        items.append(item(wfs_text, "词形变化", wfs_text))
    for key, value in parsed["web"]:
        items.append(item(value, "网络释义: " + key, value))
    return items


def main():
    q = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    app_key = os.environ.get("youdao_app_key", "").strip()
    secret = os.environ.get("youdao_app_secret", "").strip()
    if not app_key or not secret:
        output(guide_items())
        return
    if not q:
        output([error_item("请输入要翻译的内容", "中英文自动识别方向")])
        return

    if os.environ.get("split_camel", "1") == "1":
        q = util.split_token(q)
    direction = util.detect_direction(q)
    dir_key = direction[0] + ">" + direction[1]
    domain = os.environ.get("domain", "general")
    cache_dir = os.environ.get("alfred_workflow_cache", "")
    use_cache = os.environ.get("enable_cache", "1") == "1" and cache_dir
    want_dict = len(q) <= DICT_LOOKUP_MAX_CHARS

    cached = util.cache_get(cache_dir, q, dir_key) if use_cache else None
    if cached and "api" in cached:
        data, dict_info = cached["api"], cached.get("dict")
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            api_future = pool.submit(
                youdao.translate, q, direction[0], direction[1], app_key, secret, domain
            )
            dict_future = pool.submit(dictapi.lookup, q) if want_dict else None
            try:
                data = api_future.result()
            except urllib.error.URLError as e:
                output([error_item("网络请求失败", "请检查网络连接（{}）".format(e.reason))])
                return
            except OSError as e:
                output([error_item("网络请求失败", str(e))])
                return
            dict_info = dict_future.result() if dict_future else None
        code = data.get("errorCode", "")
        if code != "0":
            output([error_item(youdao.error_message(code), "原文: " + q)])
            return
        if use_cache:
            util.cache_set(cache_dir, q, dir_key, {"api": data, "dict": dict_info})

    output(build_items(youdao.parse_response(data), q, direction, dict_info))


if __name__ == "__main__":
    main()
