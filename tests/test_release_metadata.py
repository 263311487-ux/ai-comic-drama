"""Catch citation or skill version drift from the documented release."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def test_citation_and_skill_identify_the_current_changelog_release(self):
        release = re.search(r'^## (\d+\.\d+\.\d+)\s*$', (ROOT / 'CHANGELOG.md').read_text(), re.M).group(1)
        for file in ('CITATION.cff', 'SKILL.md'):
            with self.subTest(file=file):
                version = re.search(r'^\s*version:\s*(\S+)', (ROOT / file).read_text(), re.M).group(1)
                self.assertEqual(version, release, f'{file} misidentifies the release users cite or load')
