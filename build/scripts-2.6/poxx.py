 .po file so we English-bound can see what strings aren't marked 
for translation yet.

Run this with a .po file as an argument.  It will set the translated strings 
to be the same as the English, but with vowels in the wrong case:

    ./poxx.py locale/xx/LC_MESSAGES/django.po    

Then set LANGUAGE_CODE='xx' in settings.py, and you'll see wacky case for
translated strings, and normal case for strings that still need translating.

This code is in the public domain.

"""

import re, sys
import polib    # from http://bitbucket.org/izi/polib
import HTMLParser

class HtmlAwareMessageMunger(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.s = ""

    def result(self):
        return self.s

    def xform(self, s):
        return re.sub("[aeiouAEIOU]", self.munge_vowel, s)

    def munge_vowel(self, v):
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
        toks = re.split(r"(%\(\w+\)s)", data)
        for i, tok in enumerate(toks):
            if i % 2:
                self.s += tok
            else:
                self.s += self.xform(tok)

    def handle_charref(self, name):
        self.s += "&#" + name + ";"

    def handle_entityref(self, name):
        self.s += "&" + name + ";"

def munge_one_file(fname):
    po = polib.pofile(fname)
    count = 0
    for entry in po:
        hamm = HtmlAwareMessageMunger()
        hamm.feed(entry.msgid)
        entry.msgstr = hamm.result()
        if 'fuzzy' in entry.flags:
            entry.flags.remove('fuzzy') # clear the fuzzy flag
        count += 1
    print "Munged %d messages in %s" % (count, fname)
    po.save()

if __name__ == "__main__":
    for fname in sys.argv[1:]:
        munge_one_file(fname)
