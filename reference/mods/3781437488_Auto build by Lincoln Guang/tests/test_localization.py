from pathlib import Path
import tempfile
import unittest

from src.eu5autobuild.localization import (
    TranslationCatalog,
    TranslationEntry,
    load_translation_catalog,
    parse_localization,
    render_translated_localization,
    translation_report,
)


class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self.chinese = 'l_simp_chinese:\n sample_title: "标题"\n sample_desc: "说明 [Value|0]"\n'
        self.english = 'l_english:\n sample_title: "Title"\n sample_desc: "Description [Value|0]"\n'

    def test_matching_translation_is_used_and_missing_key_falls_back(self):
        catalog = TranslationCatalog(
            language="french",
            entries={
                "sample_title": TranslationEntry("标题", "Title", "Titre"),
            },
        )
        rendered = render_translated_localization(self.chinese, self.english, catalog)
        self.assertIn('sample_title: "Titre"', rendered)
        self.assertIn('sample_desc: "Description [Value|0]"', rendered)
        report = translation_report(self.chinese, self.english, catalog)
        self.assertEqual(report.translated, ("sample_title",))
        self.assertEqual(report.missing, ("sample_desc",))

    def test_changed_chinese_or_english_source_falls_back(self):
        for entry in (
            TranslationEntry("旧标题", "Title", "Titre"),
            TranslationEntry("标题", "Old title", "Titre"),
        ):
            with self.subTest(entry=entry):
                catalog = TranslationCatalog("french", {"sample_title": entry})
                rendered = render_translated_localization(self.chinese, self.english, catalog)
                self.assertIn('sample_title: "Title"', rendered)
                self.assertEqual(
                    translation_report(self.chinese, self.english, catalog).changed,
                    ("sample_title",),
                )

    def test_translation_must_preserve_markup(self):
        catalog = TranslationCatalog(
            "french",
            {
                "sample_desc": TranslationEntry(
                    "说明 [Value|0]",
                    "Description [Value|0]",
                    "Description",
                )
            },
        )
        with self.assertRaisesRegex(ValueError, "markup tokens"):
            render_translated_localization(self.chinese, self.english, catalog)

    def test_obsolete_catalog_entries_are_reported_and_not_rendered(self):
        catalog = TranslationCatalog(
            "french",
            {
                "removed_key": TranslationEntry(
                    "已删除",
                    "Removed",
                    "Supprimé",
                )
            },
        )
        rendered = render_translated_localization(self.chinese, self.english, catalog)
        self.assertNotIn("removed_key", rendered)
        self.assertEqual(
            translation_report(self.chinese, self.english, catalog).obsolete,
            ("removed_key",),
        )

    def test_catalog_loader_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "french.json"
            path.write_text(
                '{"language":"french","entries":{"sample_title":{},"sample_title":{}}}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                load_translation_catalog(path, "french")

    def test_parser_preserves_key_order(self):
        self.assertEqual(
            tuple(parse_localization(self.english, "english")),
            ("sample_title", "sample_desc"),
        )


if __name__ == "__main__":
    unittest.main()
