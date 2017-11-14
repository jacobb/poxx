# This Python file uses the following encoding: utf-8

import os
import sys
import unittest

import polib

TEST_FILE = os.path.abspath(__file__)
TEST_PATH = os.path.dirname(TEST_FILE)
MAIN_PATH = os.path.dirname(TEST_PATH)

sys.path.append(MAIN_PATH)

from poxx import munge_one_file, diff_one_file


class PoxxTestCase(unittest.TestCase):

    def setUp(self):
        self.data_path = os.path.join(TEST_PATH, 'data')

        self.sample_po_path = os.path.join(self.data_path, 'sample.po')
        self.canon_po_path = os.path.join(self.data_path, 'canon.po')
        self.sample_po = polib.pofile(self.sample_po_path)

    def tearDown(self):

        # go back to where we were
        self.sample_po.save(self.sample_po_path)


class TestMungePoFile(PoxxTestCase):

    def test_munge(self):
        munge_one_file(self.sample_po_path, blank=False)
        munged_pofile = polib.pofile(self.sample_po_path)

        self.assertEqual(munged_pofile[0].msgstr, u'Ẑḗřǿ')
        self.assertEqual(munged_pofile[1].msgstr, u'Ǿƞḗ')
        self.assertEqual(munged_pofile[2].msgstr, u'Ŧẇǿ')
        self.assertEqual(munged_pofile[3].msgstr, u'Ŧħřḗḗ')

    def test_blank_munge(self):
        munge_one_file(self.sample_po_path, blank=True)
        munged_pofile = polib.pofile(self.sample_po_path)

        self.assertEqual(munged_pofile[0].msgstr, u'')
        self.assertEqual(munged_pofile[1].msgstr, u'')
        self.assertEqual(munged_pofile[2].msgstr, u'')
        self.assertEqual(munged_pofile[3].msgstr, u'')

        untranslated_count = len(munged_pofile.untranslated_entries())
        total_count = len(munged_pofile)
        self.assertEqual(total_count, untranslated_count)

    def test_canonical_munge(self):
        munge_one_file(self.sample_po_path, blank=False, canon_name=self.canon_po_path)
        munged_pofile = polib.pofile(self.sample_po_path)

        self.assertEqual(munged_pofile[0].msgstr, u'Ẑḗřǿ')
        self.assertEqual(munged_pofile[1].msgstr, u'Uno')
        self.assertEqual(munged_pofile[2].msgstr, u'Ŧẇǿ')
        self.assertEqual(munged_pofile[3].msgstr, u'Tree')

    def test_canonical_and_blank_munge(self):
        munge_one_file(self.sample_po_path, blank=True, canon_name=self.canon_po_path)
        munged_pofile = polib.pofile(self.sample_po_path)

        self.assertEqual(munged_pofile[0].msgstr, u'')
        self.assertEqual(munged_pofile[1].msgstr, u'Uno')
        self.assertEqual(munged_pofile[2].msgstr, u'')
        self.assertEqual(munged_pofile[3].msgstr, u'Tree')

        untranslated_count = len(munged_pofile.untranslated_entries())
        self.assertEqual(2, untranslated_count)


class DiffTestCase(PoxxTestCase):

    def setUp(self):
        super().setUp()
        self.diff_path = os.path.join(self.data_path, 'sample_diff.po')

    def tearDown(self):

        super().tearDown()

        # Clean up a diff file if the test created one
        if os.path.isfile(self.diff_path):
            os.remove(self.diff_path)

    def test_diff(self):
        diff_one_file(self.sample_po_path, self.canon_po_path)
        self.assertTrue(os.path.isfile(self.diff_path))

        sample_pofile = polib.pofile(self.sample_po_path)
        diff_pofile = polib.pofile(self.diff_path)

        # Make sure our non-canonical entries are the ones in the diff
        self.assertEqual(diff_pofile[0].msgid, u'Zero')
        self.assertEqual(diff_pofile[1].msgid, u'Two')

        # all entries in a diff file should be marked as untranslated
        untranslated_count = len(diff_pofile.untranslated_entries())
        total_count = len(diff_pofile)
        self.assertEqual(total_count, untranslated_count)

        # make sure we only created a diff and didn't alter the original
        self.assertEqual(sample_pofile, self.sample_po)
