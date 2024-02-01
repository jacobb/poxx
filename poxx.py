#!/usr/bin/env python
# This Python file uses the following encoding: utf-8
"""Munge a .po file so we English-bound can see what strings aren't marked
for translation yet.

Run this with a .po file as an argument.  It will set the translated strings
to be the same as the English, but with vowels in the wrong case:

    ./poxx.py locale/xx/LC_MESSAGES/django.po

Then set LANGUAGE_CODE='xx' in settings.py, and you'll see wacky case for
translated strings, and normal case for strings that still need translating.

This code is in the public domain.

"""


import optparse
import os.path
import re
import polib    # from http://bitbucket.org/izi/polib
from html.parser import HTMLParser

VERSION_STR = '2.0.0'


class HtmlAwareMessageMunger(HTMLParser):

    # Lifted from http://translate.sourceforge.net
    ORIGINAL = u"ABCDEFGHIJKLMNOPQRSTUVWXYZ" + u"abcdefghijklmnopqrstuvwxyz"
    REWRITE_UNICODE_MAP = u"ȦƁƇḒḖƑƓĦĪĴĶĿḾȠǾƤɊŘŞŦŬṼẆẊẎẐ" + u"ȧƀƈḓḗƒɠħīĵķŀḿƞǿƥɋřşŧŭṽẇẋẏẑ"

    PLACEHOLDER_REGEX = re.compile(
        r"((?:%(?:\(\w+\))?[-+]?[\d.]*[sfd])|(?:\{\w+[:]?[\d.]*[sfd]?\}))"
    )

    def __init__(self):
        super().__init__()
        self.s = ""

    def result(self):
        return self.s

    def xform(self, s):

        # return re.sub("[aeiouAEIOU]", self.munge_vowel, s)
        return re.sub("[A-Za-z]", self.munge_unicode, s)

    def munge_unicode(self, x):
        return self.REWRITE_UNICODE_MAP[self.ORIGINAL.find(x.group(0))]

    def munge_vowel(self, v):
        "Kept for historical reasons"
        v = v.group(0)
        if v.isupper():
            return v.lower()
        else:
            return v.upper()

    def handle_starttag(self, tag, attrs, closed=False):
        self.s += "<" + tag
        for name, val in attrs:
            self.s += " "
            self.s += name
            self.s += '="'
            if name in ['alt', 'title']:
                self.s += self.xform(val)
            else:
                if val is None:
                    val = ""
                self.s += val
            self.s += '"'
        if closed:
            self.s += " /"
        self.s += ">"

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs, closed=True)

    def handle_endtag(self, tag):
        self.s += "</" + tag + ">"

    def handle_data(self, data):
        # We don't want to munge placeholders, so split on them, keeping them
        # in the list, then xform every other token.
        toks = self.PLACEHOLDER_REGEX.split(data)
        for i, tok in enumerate(toks):
            if i % 2:
                self.s += tok
            else:
                self.s += self.xform(tok)

    def handle_charref(self, name):
        self.s += "&#" + name + ";"

    def handle_entityref(self, name):
        self.s += "&" + name + ";"


def _get_canonical_value(canonical_po, msgid):
    if canonical_po is None:
        return None
    canonical_entry = canonical_po.find(msgid)
    return getattr(canonical_entry, 'msgstr', None)


def munge_one_file(fname, blank, canon_name=None):
    po = polib.pofile(fname)
    canonical_po = polib.pofile(canon_name) if canon_name else None

    count = 0
    for entry in po:
        canonical_value = _get_canonical_value(canonical_po, entry.msgid)

        if canonical_value:
            entry.msgstr = canonical_value
        elif blank:
            entry.msgstr = ''
        else:
            hamm = HtmlAwareMessageMunger()
            hamm.feed(entry.msgid)
            entry.msgstr = hamm.result()

            if 'fuzzy' in entry.flags:
                entry.flags.remove('fuzzy')  # clear the fuzzy flag
        count += 1

    po.save()

    return "Munged %d messages in %s" % (count, fname)


def diff_one_file(fname, canon_name):
    po = polib.pofile(fname)
    canonical_po = polib.pofile(canon_name)
    diff_po = polib.POFile()
    po.merge(canonical_po)

    # msgids in the def. po file with no cananonical definition are
    # marked as obsolute after a merge
    for entry in po.obsolete_entries():
        entry.msgstr = ''
        entry.obsolete = False
        diff_po.append(entry)

    # Add any msgids that are untranslated in the
    # canonical catalog as well
    for entry in canonical_po.untranslated_entries():
        entry.msgstr = ''
        diff_po.append(entry)

    full_fname_path = os.path.abspath(fname)
    fname_dir = os.path.dirname(full_fname_path)
    fname_name = os.path.basename(full_fname_path).replace('.po', '')  # no extension
    diff_po_path = os.path.join(fname_dir, '%s_diff.po' % fname_name)
    diff_po.save(diff_po_path)
    return "Created %s with %s translations" % (diff_po_path, len(diff_po))


if __name__ == "__main__":
    p = optparse.OptionParser(
        usage='%prog <po_file> [<another_po_file, ..] [-d] [-c] [-b]',
        version='%prog ' + VERSION_STR)

    p.add_option('--canonical', '-c',
        help="replace msgids from canonical .po file",
        dest='canonical_po_file')
    p.add_option(
        '--diff', '-d',
        action='store_true',
        dest='diff',
        help='create a po file with msgids not translated in canonical po file')
    p.add_option('--blank', '-b',
        help="mark as untranslated where a msgstr would be munged",
        action='store_true',
        dest='blank')

    options, po_files = p.parse_args()

    for fname in po_files:
        if options.diff and not options.canonical_po_file:
            raise ValueError('--canonical is required when creating a diff')

        if options.diff:
            report_msg = diff_one_file(fname, options.canonical_po_file)
        else:
            report_msg = munge_one_file(fname, options.blank, canon_name=options.canonical_po_file)
