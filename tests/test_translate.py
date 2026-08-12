import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import translate
from test_parse import FULL_WORD_RESPONSE, SENTENCE_RESPONSE

import youdao


class TestGuideItems(unittest.TestCase):
    def test_missing_key_gives_two_openurl_items(self):
        items = translate.guide_items()
        self.assertEqual(len(items), 2)
        for it in items:
            self.assertEqual(it["variables"]["action"], "open_url")
        self.assertIn("ai.youdao.com", items[0]["variables"]["url"])
        self.assertIn("alfredpreferences://", items[1]["variables"]["url"])


class TestBuildItems(unittest.TestCase):
    def test_word_items(self):
        parsed = youdao.parse_response(FULL_WORD_RESPONSE)
        items = translate.build_items(parsed, "hello", ("auto", "zh-CHS"))
        main = items[0]
        self.assertEqual(main["title"], "你好")
        self.assertEqual(main["arg"], "你好")
        self.assertIn("hello", main["subtitle"])
        self.assertIn("美:", main["subtitle"])  # 音标内联在 subtitle
        # 修饰键：⌘ 本地发音 / ⌥ 在线发音，发音内容为英文侧文本
        self.assertEqual(main["mods"]["cmd"]["variables"]["action"], "speak_local")
        self.assertEqual(main["mods"]["cmd"]["arg"], "hello")
        self.assertEqual(main["mods"]["alt"]["variables"]["action"], "speak_online")
        self.assertEqual(
            main["mods"]["alt"]["variables"]["speak_url"], parsed["speech_us"]
        )
        # 词典释义 + 词形 + 网络释义都在
        titles = [it["title"] for it in items]
        self.assertIn("int. 喂；哈罗", titles)
        self.assertTrue(any("复数: hellos" in t for t in titles))
        self.assertTrue(any("你好世界" in t for t in titles))

    def test_sentence_items(self):
        parsed = youdao.parse_response(SENTENCE_RESPONSE)
        items = translate.build_items(
            parsed, "how are you doing today", ("auto", "zh-CHS")
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "你今天过得怎么样")
        # 无 us-speech 时在线发音回退 tSpeakUrl
        self.assertEqual(
            items[0]["mods"]["alt"]["variables"]["speak_url"],
            SENTENCE_RESPONSE["tSpeakUrl"],
        )

    def test_zh_to_en_speaks_translation(self):
        parsed = youdao.parse_response(
            {"errorCode": "0", "translation": ["hello"], "tSpeakUrl": "http://t"}
        )
        items = translate.build_items(parsed, "你好", ("zh-CHS", "en"))
        # 中译英时英文侧是译文，发音应读译文
        self.assertEqual(items[0]["mods"]["cmd"]["arg"], "hello")
        self.assertEqual(items[0]["mods"]["cmd"]["variables"]["speak_lang"], "en")


class TestDictDefs(unittest.TestCase):
    DICT_INFO = {
        "phonetic_us": "rʌn",
        "phonetic_uk": "rʌn",
        "defs": ["v. 跑，奔跑；管理，经营", "n. 跑步，赛跑；旅程"],
    }

    def test_defs_add_one_item_per_pos(self):
        parsed = youdao.parse_response({"errorCode": "0", "translation": ["跑"]})
        items = translate.build_items(parsed, "run", ("auto", "zh-CHS"), self.DICT_INFO)
        titles = [it["title"] for it in items]
        self.assertIn("v. 跑，奔跑；管理，经营", titles)
        self.assertIn("n. 跑步，赛跑；旅程", titles)

    def test_phonetic_fallback_from_dict(self):
        # openapi 已不返回音标，主条目 subtitle 应回退用 jsonapi 的音标
        parsed = youdao.parse_response({"errorCode": "0", "translation": ["跑"]})
        items = translate.build_items(parsed, "run", ("auto", "zh-CHS"), self.DICT_INFO)
        self.assertIn("美: rʌn", items[0]["subtitle"])

    def test_all_items_use_translate_icon(self):
        parsed = youdao.parse_response(FULL_WORD_RESPONSE)
        items = translate.build_items(parsed, "hello", ("auto", "zh-CHS"), self.DICT_INFO)
        for it in items:
            self.assertEqual(it["icon"]["path"], "icons/translate.png")


class TestErrorItem(unittest.TestCase):
    def test_error_item_invalid(self):
        it = translate.error_item("签名校验失败", "请检查密钥")
        self.assertFalse(it["valid"])
        self.assertEqual(it["title"], "签名校验失败")

    def test_error_item_no_warning_icon(self):
        # 用户要求：不出现黄色三角，统一用翻译图标
        it = translate.error_item("网络请求失败")
        self.assertEqual(it["icon"]["path"], "icons/translate.png")
        for g in translate.guide_items():
            self.assertEqual(g["icon"]["path"], "icons/translate.png")


if __name__ == "__main__":
    unittest.main()
