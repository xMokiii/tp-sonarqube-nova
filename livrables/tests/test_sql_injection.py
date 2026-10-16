"""Teste sqli_medium avec SQLite en memoire, sans lancer Flask ni ouvrir TIWAP.db."""

import importlib.util
from pathlib import Path
import sqlite3
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


SQLI_PATH = Path(__file__).resolve().parents[1] / "TIWAP" / "vulnerabilities" / "SQLi.py"


class SQLInjectionTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.execute(
            "CREATE TABLE users (userid INTEGER PRIMARY KEY, username TEXT)"
        )
        self.connection.executemany(
            "INSERT INTO users VALUES (?, ?)", [(1, "alice"), (2, "bob")]
        )

        # Remplace seulement l'acces a la base ; le code SQL teste est celui de TIWAP.
        manager_module = ModuleType("helper.db_manager")
        manager_module.DBManager = lambda: SimpleNamespace(
            get_db_connection=lambda: self.connection
        )
        spec = importlib.util.spec_from_file_location("tiwap_sqli_test", SQLI_PATH)
        self.sqli = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"helper.db_manager": manager_module}):
            spec.loader.exec_module(self.sqli)

    def test_existing_user(self):
        self.assertEqual(self.sqli.sqli_medium("1"), [(1, "alice")])

    def test_unknown_user(self):
        self.assertEqual(self.sqli.sqli_medium("999"), [])

    def test_quote_is_treated_as_data(self):
        self.assertEqual(self.sqli.sqli_medium("1'"), [])

    def test_injection_cannot_return_other_users(self):
        self.assertEqual(self.sqli.sqli_medium("1' OR '1'='1"), [])


if __name__ == "__main__":
    unittest.main()
