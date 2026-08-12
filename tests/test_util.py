import os
import sys
import time
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import util


class TestDetectDirection(unittest.TestCase):
    def test_pure_english(self):
        self.assertEqual(util.detect_direction("hello world"), ("auto", "zh-CHS"))

    def test_pure_chinese(self):
        self.assertEqual(util.detect_direction("你好"), ("zh-CHS", "en"))

    def test_chinese_with_punctuation_and_digits(self):
        # 参考版的缺陷用例：含标点/数字的中文句子必须仍判为中文
        self.assertEqual(util.detect_direction("圆周率是 3.14。"), ("zh-CHS", "en"))

    def test_mixed_chinese_english(self):
        # 含任意 CJK 字符即判中文 → 译英
        self.assertEqual(util.detect_direction("你好world"), ("zh-CHS", "en"))

    def test_english_with_symbols(self):
        self.assertEqual(util.detect_direction("machine-learning!"), ("auto", "zh-CHS"))


class TestSplitToken(unittest.TestCase):
    def test_camel_case(self):
        self.assertEqual(util.split_token("helloWorld"), "hello World")

    def test_acronym_preserved(self):
        # 参考版的缺陷用例：不能把连续大写缩略词拆碎
        self.assertEqual(util.split_token("API"), "API")
        self.assertEqual(util.split_token("getHTTPServer"), "get HTTP Server")

    def test_snake_case(self):
        self.assertEqual(util.split_token("snake_case_name"), "snake case name")

    def test_multi_word_untouched(self):
        # 已含空格的查询不做拆词
        self.assertEqual(util.split_token("hello world"), "hello world")

    def test_chinese_untouched(self):
        self.assertEqual(util.split_token("你好"), "你好")


class TestCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_miss_then_hit(self):
        self.assertIsNone(util.cache_get(self.tmp.name, "hello", "auto>zh-CHS"))
        util.cache_set(self.tmp.name, "hello", "auto>zh-CHS", {"translation": ["你好"]})
        self.assertEqual(
            util.cache_get(self.tmp.name, "hello", "auto>zh-CHS"),
            {"translation": ["你好"]},
        )

    def test_direction_isolated(self):
        util.cache_set(self.tmp.name, "hello", "auto>zh-CHS", {"translation": ["你好"]})
        self.assertIsNone(util.cache_get(self.tmp.name, "hello", "zh-CHS>en"))

    def test_expired(self):
        util.cache_set(self.tmp.name, "hello", "auto>zh-CHS", {"translation": ["你好"]})
        self.assertIsNone(
            util.cache_get(self.tmp.name, "hello", "auto>zh-CHS", ttl=0)
        )

    def test_missing_dir_is_safe(self):
        missing = os.path.join(self.tmp.name, "not-exist")
        self.assertIsNone(util.cache_get(missing, "hello", "auto>zh-CHS"))
        # cache_set 应自动建目录且不抛异常
        util.cache_set(missing, "hello", "auto>zh-CHS", {"a": 1})
        self.assertEqual(util.cache_get(missing, "hello", "auto>zh-CHS"), {"a": 1})


if __name__ == "__main__":
    unittest.main()
