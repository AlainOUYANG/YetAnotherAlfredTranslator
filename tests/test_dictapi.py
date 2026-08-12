import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dictapi

# dict.youdao.com/jsonapi 实测响应精简样本（2026-08-11）
EC_RESPONSE = {
    "ec": {
        "word": [
            {
                "usphone": "rʌn",
                "ukphone": "rʌn",
                "trs": [
                    {"tr": [{"l": {"i": ["v. 跑，奔跑；管理，经营"]}}]},
                    {"tr": [{"l": {"i": ["n. 跑步，赛跑；旅程"]}}]},
                    {"tr": [{"l": {"i": ["【名】 （Run）（塞）鲁恩（人名）"]}}]},
                ],
            }
        ]
    }
}

CE_RESPONSE = {
    "ce": {
        "word": [
            {
                "trs": [
                    {
                        "tr": [
                            {
                                "l": {
                                    "i": [
                                        "",
                                        {"#text": "causal", "@action": "link"},
                                        " ",
                                        {"#text": "inference", "@action": "link"},
                                    ],
                                    "#tran": "因果推断：确定事件间的因果关系",
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
}


class TestParseEc(unittest.TestCase):
    def test_multiple_pos_defs(self):
        r = dictapi.parse_jsonapi(EC_RESPONSE)
        self.assertEqual(r["phonetic_us"], "rʌn")
        self.assertEqual(r["phonetic_uk"], "rʌn")
        self.assertEqual(
            r["defs"],
            [
                "v. 跑，奔跑；管理，经营",
                "n. 跑步，赛跑；旅程",
                "【名】 （Run）（塞）鲁恩（人名）",
            ],
        )


class TestParseCe(unittest.TestCase):
    def test_link_text_joined_with_tran(self):
        r = dictapi.parse_jsonapi(CE_RESPONSE)
        self.assertIsNone(r["phonetic_us"])
        self.assertEqual(r["defs"], ["causal inference — 因果推断：确定事件间的因果关系"])


class TestDefensive(unittest.TestCase):
    def test_empty_response(self):
        r = dictapi.parse_jsonapi({})
        self.assertEqual(r["defs"], [])
        self.assertIsNone(r["phonetic_us"])


if __name__ == "__main__":
    unittest.main()
