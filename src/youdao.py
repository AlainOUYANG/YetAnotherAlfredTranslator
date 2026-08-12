"""有道智云文本翻译 API 客户端（v3 签名）。仅用标准库。

签名规范：https://ai.youdao.com/DOCSIRMA/html/trans/api/wbfy/index.html
"""
import hashlib
import json
import time
import urllib.parse
import urllib.request
import uuid

API_URL = "https://openapi.youdao.com/api"

ERROR_MESSAGES = {
    "101": "缺少必填参数",
    "102": "不支持的语言类型",
    "103": "翻译文本过长",
    "108": "appKey 无效，请检查应用 ID",
    "113": "查询内容不能为空",
    "202": "签名校验失败，请检查应用密钥",
    "401": "账户已欠费，请前往有道智云控制台充值",
    "411": "访问频率受限，请稍后重试",
}


def truncate(q):
    return q if len(q) <= 20 else q[:10] + str(len(q)) + q[-10:]


def sign(app_key, q, salt, curtime, secret):
    raw = app_key + truncate(q) + salt + curtime + secret
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_params(q, from_, to, app_key, secret, domain="general"):
    salt = str(uuid.uuid4())
    curtime = str(int(time.time()))
    return {
        "q": q,
        "from": from_,
        "to": to,
        "appKey": app_key,
        "salt": salt,
        "sign": sign(app_key, q, salt, curtime, secret),
        "signType": "v3",
        "curtime": curtime,
        "domain": domain,
    }


# 有道为国内服务，直连即可；urllib 默认会读 macOS 系统代理（Clash 等），
# 走本地代理反而容易握手超时，故显式绕过代理。
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def translate(q, from_, to, app_key, secret, domain="general", timeout=6):
    """请求翻译，返回原始响应 dict。网络异常向上抛出。"""
    data = urllib.parse.urlencode(
        build_params(q, from_, to, app_key, secret, domain)
    ).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, method="POST")
    with _OPENER.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_response(data):
    """防御式提取响应字段为扁平结构，缺失字段为 None 或 []。"""
    basic = data.get("basic") or {}
    translation = data.get("translation") or []
    wfs = []
    for item in basic.get("wfs") or []:
        wf = item.get("wf") or {}
        if wf.get("name") and wf.get("value"):
            wfs.append((wf["name"], wf["value"]))
    web = []
    for item in data.get("web") or []:
        if item.get("key") and item.get("value"):
            web.append((item["key"], "；".join(item["value"])))
    return {
        "translation": translation[0] if translation else None,
        "phonetic": basic.get("phonetic"),
        "phonetic_us": basic.get("us-phonetic"),
        "phonetic_uk": basic.get("uk-phonetic"),
        "speech_us": basic.get("us-speech"),
        "speech_uk": basic.get("uk-speech"),
        "explains": basic.get("explains") or [],
        "wfs": wfs,
        "web": web,
        "t_speak_url": data.get("tSpeakUrl"),
    }


def error_message(code):
    return ERROR_MESSAGES.get(code, "有道 API 错误（错误码 {}）".format(code))
