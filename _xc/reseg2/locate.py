# -*- coding: utf-8 -*-
"""Locate corpus paragraphs and side-map material IN THE PRINTED LINE STREAM.

The whole point: every side-map check in b2/ and b3/ is decided by PRINTED
ORDER, read off the page, not by the ordinal arithmetic that built the remap.
That is what makes the check independent of the thing it checks.

`letters()` is reseg.py's own alphabet filter, unchanged.
"""
import re, bisect

ALPHA = re.compile(r'[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]')


def letters(s):
    return ALPHA.sub('', s or '')


class Page(object):
    """The printed line stream as one letter string, with a letter -> line map."""

    def __init__(self, stream):
        self.stream = stream
        buf = []
        starts = []
        pos = 0
        for it in stream:
            starts.append(pos)
            t = letters(it[3])
            buf.append(t)
            pos += len(t)
        self.text = ''.join(buf)
        self.starts = starts
        self.starts.append(pos)

    def line_of(self, letter_pos):
        k = bisect.bisect_right(self.starts, letter_pos) - 1
        return max(0, min(k, len(self.stream) - 1))

    def find(self, s, frm=0):
        t = letters(s)
        if not t:
            return -1
        return self.text.find(t, frm)

    def span(self, s, frm=0):
        """(first_line, last_line, letter_start, letter_end) or None."""
        t = letters(s)
        if not t:
            return None
        i = self.text.find(t, frm)
        if i < 0:
            return None
        return (self.line_of(i), self.line_of(i + len(t) - 1), i, i + len(t))
