import tempfile
import unittest
from pathlib import Path
from tidydesk import DEFAULT_RULES, find_duplicates, organize_folder, undo_last


class TestTidyDesk(unittest.TestCase):
    def test_organize_and_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "report.pdf").write_text("pdf data", encoding="utf-8")
            (root / "photo.png").write_text("img data", encoding="utf-8")

            moves = organize_folder(root, DEFAULT_RULES, dry_run=False)
            self.assertEqual(len(moves), 2)
            self.assertTrue((root / "Documents" / "report.pdf").exists())
            self.assertTrue((root / "Images" / "photo.png").exists())

            restored = undo_last(root)
            self.assertEqual(restored, 2)
            self.assertTrue((root / "report.pdf").exists())
            self.assertTrue((root / "photo.png").exists())

    def test_find_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("same content", encoding="utf-8")
            (root / "b.txt").write_text("same content", encoding="utf-8")
            (root / "c.txt").write_text("different", encoding="utf-8")

            dupes = find_duplicates(root)
            self.assertEqual(len(dupes), 1)
            self.assertEqual(len(next(iter(dupes.values()))), 2)


if __name__ == "__main__":
    unittest.main()
