#!/usr/bin/env python2
# encoding: utf-8

import sys
from datetime import datetime
try:
    from sortsmill import ffcompat as fontforge
except ImportError:
    import fontforge

arabic = fontforge.open(sys.argv[1])
arabic.em = 1000

latin = fontforge.open(sys.argv[1].replace("arefruqaa", "eulertext"))

for glyph in arabic.glyphs():
    if glyph.unicode < 0x0600 and glyph.unicode != -1 and glyph.unicode != ord(" "):
        arabic.removeGlyph(glyph)

for glyph in latin.glyphs():
    if glyph.unicode > ord("~") or glyph.unicode == -1:
        latin.removeGlyph(glyph)

arabic.mergeFonts(latin)

# Set metadata
arabic.version = sys.argv[3]
years = datetime.now().year == 2015 and 2015 or "2015-%s" % datetime.now().year

arabic.copyright = ". ".join(["Portions copyright © %s, Khaled Hosny (<khaledhosny@eglug.org>)",
                              "Portions " + latin.copyright[0].lower() + latin.copyright[1:].replace("(c)", "©")])
arabic.copyright = arabic.copyright % years

en = "English (US)"
arabic.appendSFNTName(en, "Designer", "Abdoulla Aref")
arabic.appendSFNTName(en, "License URL", "http://scripts.sil.org/OFL")
arabic.appendSFNTName(en, "License", 'This Font Software is licensed under the SIL Open Font License, Version 1.1. \
This Font Software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR \
CONDITIONS OF ANY KIND, either express or implied. See the SIL Open Font License \
for the specific language, permissions and limitations governing your use of \
this Font Software.')
arabic.appendSFNTName(en, "Descriptor", "Aref Ruqaa is an Arabic typeface that aspires to capture the essence of \
the classical Ruqaa calligraphic style.")
arabic.appendSFNTName(en, "Sample Text", "الخط هندسة روحانية ظهرت بآلة جسمانية")

arabic.generate(sys.argv[2], flags=("round", "opentype"))
