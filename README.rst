====
Poxx
====

This is a fork of Ned Batchelder (@nedbat)'s wonderful poxx tool for stubbing out translations in .po files.

The original can be found here: http://nedbatchelder.com/blog/201012/faked_translations_poxxpy.html

Why Fork
========

#) I wanted to add something to allow for CSS'd upper-case text to be clearly marked as translated
#) I wanted an easy pip-able url for multiple virtualenvs.

How is it different than the original?
======================================
* Flags have been added for working with data that needs to be partially stubbed out. See ``flags`` for more information
* A bit of code lifted from http://translate.sourceforge.net now "translates" msgids into a unicode-character equivilient. This preserves case and allows for CSS-controled casing to be clearly marked as translated.


Usage
=====
**poxx.py <po_filename>**

Where ``po_filename`` is one or many .po files with translations you wish to stub out.

.. _flags:
Flags
-----
.. _canonical_flag:
**-c <canonical_po_file>, --canonaical=<canonical_po_file>**

Specify a .po file to use as a canonical source of translations. If specified, poxx will look to see if a msgid is in the canonical_po file before stubbing it out. If it is, the corresponding msgstr will be used instead of the stub string.

**--diff, -d**

Must be used with ``canonical_flag``.

Create a diff file containing all msgids found in the specified po file, but not in the ``canonical_po_file``.

**--blank, -b**

Where a msgstr would be stubbed, mark as untranslated instead.