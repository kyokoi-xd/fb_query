import unittest
import os
import json
from fb_query import load_config


class TestLoadConfig(unittest.TestCase):
    def setUp(self):
        with open("test_config.json", "w", encoding="utf-8") as f:
            json.dump({"host": "localhost", "database": "TEST1.fdb", "user": "SYSDBA", "password": "masterkey", "charset": "utf-8"}, f)

    def tearDown(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")

    def test_load_valid_config(self):
        config = load_config('test_config.json')
        self.assertEqual(config["host"], "localhost")
        self.assertEqual(config["database"], "TEST1.fdb")

    def test_load_missing_config(self):
        with self.assertRaises(FileNotFoundError):
            load_config("missing_config.json")

    def test_load_empty_config(self):
        with open("empty_config.json", "w", encoding="utf-8") as f:
            pass
        with self.assertRaises(ValueError):
            load_config("empty_config.json")
        os.remove("empty_config.json")