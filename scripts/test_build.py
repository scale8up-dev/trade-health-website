"""Regression tests for clean, repeated and Netlify-prepared build directories."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def setUp(self):
        results = ROOT / "test-results"
        results.mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(prefix="build-fixture-", dir=results)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts/build.py", self.root / "scripts/build.py")
        for source in ROOT.iterdir():
            if source.is_file() and (
                source.suffix in {".html", ".css", ".js", ".webp", ".svg", ".jpg", ".txt", ".xml", ".toml"}
                or source.name in {"_headers", "_redirects"}
            ):
                shutil.copy2(source, self.root / source.name)

    def build(self):
        return subprocess.run([sys.executable, "scripts/build.py"], cwd=self.root, capture_output=True, text=True)

    def assert_public_package(self):
        with zipfile.ZipFile(self.root / "tradehealth-netlify.zip") as archive:
            names = set(archive.namelist())
        self.assertEqual(len(names), 22)
        self.assertIn("index.html", names)
        self.assertNotIn("netlify.toml", names)
        self.assertNotIn("START_HERE.txt", names)
        self.assertEqual(names, {file.name for file in (self.root / "dist").iterdir()})
        self.assertIn("https://formspree.io", (self.root / "dist/_headers").read_text())

    def test_clean_and_repeated_build(self):
        for _ in range(2):
            result = self.build()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assert_public_package()

    def test_netlify_metadata_does_not_block_or_get_published(self):
        output = self.root / "dist"
        output.mkdir()
        (output / "netlify.toml").write_text("# Netlify-generated build metadata\n")
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_public_package()

    def test_unexpected_files_still_block_without_being_deleted(self):
        output = self.root / "dist"
        output.mkdir()
        unknown = output / "unrelated.txt"
        unknown.write_text("Preserve this file")
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unexpected files", result.stderr)
        self.assertEqual(unknown.read_text(), "Preserve this file")


if __name__ == "__main__":
    unittest.main()
