#!/usr/bin/env python2
# encoding: utf-8

import argparse
from datetime import datetime
from sortsmill import ffcompat as fontforge

def merge(args):
    version = args.version
    arabicfilename = args.arabicfile
    latinfilename = args.latinfile

    arabic = fontforge.open(arabicfilename)
    arabic.encoding = "Unicode"

    latin = fontforge.open(latinfilename)
    latin.em = arabic.em
    latin.encoding = "Unicode"

    for glyph in arabic.glyphs():
        if glyph.unicode < 0x0600 and glyph.unicode != -1 and glyph.unicode != ord(" "):
            arabic.removeGlyph(glyph)

    for glyph in latin.glyphs():
        if glyph.unicode > ord("~") or glyph.unicode == -1:
            latin.removeGlyph(glyph)

    arabic.mergeFonts(latin)

    # Set metadata
    arabic.version = version
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

    # Handle mixed outlines and references
    arabic.selection.all()
    arabic.correctReferences()
    arabic.selection.none()

    return arabic

def main():
    parser = argparse.ArgumentParser(description="Create a version of Amiri with colored marks using COLR/CPAL tables.")
    parser.add_argument("arabicfile", metavar="FILE", help="input font to process")
    parser.add_argument("latinfile", metavar="FILE", help="input font to process")
    parser.add_argument("--out-file", metavar="FILE", help="output font to write", required=True)
    parser.add_argument("--version", metavar="version", help="version number", required=True)
    parser.add_argument("--no-glyphnames", action="store_true", help="don't generate glyph names")

    args = parser.parse_args()

    font = merge(args)

    flags = ["round", "opentype"]
    if args.no_glyphnames:
        flags.append("short-post")

    font.generate(args.out_file, flags=flags)

if __name__ == "__main__":
    main()
