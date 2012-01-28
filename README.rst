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

A bit of code lifted from http://translate.sourceforge.net now "translates" msgids into a unicode-character equivilient. This preserves case and allows for CSS-controled casing to be clearly marked as translated.
