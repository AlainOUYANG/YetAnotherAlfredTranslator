import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import youdao

# 有道 API 单词查询的典型响应（据官方文档与旧版 Workflow 实际返回整理）
FULL_WORD_RESPONSE = {
    "errorCode": "0",
    "query": "hello",
    "translation": ["你好"],
    "basic": {
        "phonetic": "həˈləʊ",
        "us-phonetic": "həˈloʊ",
        "uk-phonetic": "həˈləʊ",
        "us-speech": "https://openapi.youdao.com/ttsapi?q=hello&type=us",
        "uk-speech": "https://openapi.youdao.com/ttsapi?q=hello&type=uk",
        "explains": ["int. 喂；哈罗", "n. 表示问候"],
        "wfs": [{"wf": {"name": "复数", "value": "hellos"}}],
    },
    "web": [
        {"key": "Hello World", "value": ["你好世界", "举世震惊"]},
        {"key": "hello kitty", "value": ["凯蒂猫"]},
    ],
    "tSpeakUrl": "https://openapi.youdao.com/ttsapi?q=%E4%BD%A0%E5%A5%BD",
    "dict": {"url": "yddict://m.youdao.com/dict?le=eng&q=hello"},
}

# 长句翻译：无 basic/web 字段
SENTENCE_RESPONSE = {
    "errorCode": "0",
    "query": "how are you doing today",
    "translation": ["你今天过得怎么样"],
    "tSpeakUrl": "https://openapi.youdao.com/ttsapi?q=x",
}


class TestParseResponse(unittest.TestCase):
    def test_full_word(self):
        r = youdao.parse_response(FULL_WORD_RESPONSE)
        self.assertEqual(r["translation"], "你好")
        self.assertEqual(r["phonetic_us"], "həˈloʊ")
        self.assertEqual(r["phonetic_uk"], "həˈləʊ")
        self.assertEqual(r["speech_us"], "https://openapi.youdao.com/ttsapi?q=hello&type=us")
        self.assertEqual(r["explains"], ["int. 喂；哈罗", "n. 表示问候"])
        self.assertEqual(r["wfs"], [("复数", "hellos")])
        self.assertEqual(
            r["web"],
            [("Hello World", "你好世界；举世震惊"), ("hello kitty", "凯蒂猫")],
        )
        self.assertEqual(r["t_speak_url"], "https://openapi.youdao.com/ttsapi?q=%E4%BD%A0%E5%A5%BD")

    def test_sentence_without_dict_fields(self):
        r = youdao.parse_response(SENTENCE_RESPONSE)
        self.assertEqual(r["translation"], "你今天过得怎么样")
        self.assertIsNone(r["phonetic_us"])
        self.assertIsNone(r["speech_us"])
        self.assertEqual(r["explains"], [])
        self.assertEqual(r["wfs"], [])
        self.assertEqual(r["web"], [])

    def test_empty_translation_defensive(self):
        r = youdao.parse_response({"errorCode": "0"})
        self.assertIsNone(r["translation"])


class TestErrorMessage(unittest.TestCase):
    def test_known_codes(self):
        self.assertIn("签名", youdao.error_message("202"))
        self.assertIn("欠费", youdao.error_message("401"))
        self.assertIn("频率", youdao.error_message("411"))

    def test_unknown_code_includes_code(self):
        self.assertIn("999", youdao.error_message("999"))


if __name__ == "__main__":
    unittest.main()
