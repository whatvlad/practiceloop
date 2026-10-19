import unittest

from check_content import inspect

from app.content.catalogue import TEXT


class ContentTests(unittest.TestCase):
    def test_catalogue_passes(self):
        self.assertEqual(inspect(dict(TEXT)), [])

    def test_critical_and_score_failures_identify_keys(self):
        for replacement in (
            "{expression}",
            "The thing is there.",
            "Calculate " + "word " * 22 + ".",
            "Calculate the primitive.",
            42,
            "Calculate",
        ):
            entries = dict(TEXT)
            entries["calculate"] = replacement
            self.assertTrue(any("calculate:" in failure for failure in inspect(entries)))

    def test_missing_and_extra_keys_fail(self):
        entries = dict(TEXT)
        entries.pop("calculate")
        entries["unknown"] = "Calculate."
        failures = inspect(entries)
        self.assertTrue(any("calculate:" in failure for failure in failures))
        self.assertTrue(any("unknown:" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
