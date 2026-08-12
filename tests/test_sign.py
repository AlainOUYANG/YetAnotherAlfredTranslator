import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import youdao


class TestTruncate(unittest.TestCase):
    def test_short_text_unchanged(self):
        self.assertEqual(youdao.truncate("hello"), "hello")

    def test_exactly_20_unchanged(self):
        q = "a" * 20
        self.assertEqual(youdao.truncate(q), q)

    def test_long_text_truncated(self):
        q = "a" * 21
        self.assertEqual(youdao.truncate(q), "a" * 10 + "21" + "a" * 10)

    def test_truncate_counts_characters_not_bytes(self):
        q = "中" * 25
        self.assertEqual(youdao.truncate(q), "中" * 10 + "25" + "中" * 10)


class TestSign(unittest.TestCase):
    # 期望值为 sha256(appKey + input + salt + curtime + secret) 的预计算常量
    def test_short_text_sign(self):
        self.assertEqual(
            youdao.sign("testKey", "hello", "salt123", "1600000000", "testSecret"),
            "d8c3922c65198a8e7a613ded32c95943a3e16c44fafe058b10b7c669f40f3e69",
        )

    def test_long_text_sign_uses_truncated_input(self):
        self.assertEqual(
            youdao.sign("testKey", "a" * 21, "salt123", "1600000000", "testSecret"),
            "c76ceed9fa57b48af71d66d0fde928051165286e093a31022d9902ce2d10e2f3",
        )


class TestBuildParams(unittest.TestCase):
    def test_v3_required_fields(self):
        p = youdao.build_params("hello", "auto", "zh-CHS", "k", "s", domain="computers")
        self.assertEqual(p["q"], "hello")
        self.assertEqual(p["from"], "auto")
        self.assertEqual(p["to"], "zh-CHS")
        self.assertEqual(p["appKey"], "k")
        self.assertEqual(p["signType"], "v3")
        self.assertEqual(p["domain"], "computers")
        self.assertNotIn("secret", p.values())
        # sign 可由参数自身复原验证
        self.assertEqual(
            p["sign"], youdao.sign("k", "hello", p["salt"], p["curtime"], "s")
        )


if __name__ == "__main__":
    unittest.main()
