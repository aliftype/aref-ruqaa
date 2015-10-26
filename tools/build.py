#!/usr/bin/env python2
# encoding: utf-8

import argparse
import string
from datetime import datetime
from sortsmill import ffcompat as fontforge

def merge(args):
    arabic = fontforge.open(args.arabicfile)
    arabic.encoding = "Unicode"

    with open(args.feature_file) as feature_file:
        features = string.Template(feature_file.read())
        gpos = arabic.generateFeatureString()
        for lookup in arabic.gpos_lookups:
            arabic.removeLookup(lookup)
        arabic.mergeFeatureString(features.substitute(GPOS=gpos))

    latin = fontforge.open(args.latinfile)
    latin.encoding = "Unicode"
    latin.em = arabic.em

    latin_locl = ""
    for glyph in latin.glyphs():
        if glyph.color == 0xff0000:
            latin.removeGlyph(glyph)
        else:
            if glyph.glyphname in arabic:
                name = glyph.glyphname
                glyph.unicode = -1
                glyph.glyphname = name + ".latin"
                if not latin_locl:
                    latin_locl = "feature locl {lookupflag IgnoreMarks; script latn;"
                latin_locl += "sub %s by %s;" % (name, glyph.glyphname)

    arabic.mergeFonts(latin)
    if latin_locl:
        latin_locl += "} locl;"
        arabic.mergeFeatureString(latin_locl)

    # Set metadata
    arabic.version = args.version
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

    return arabic

def main():
    parser = argparse.ArgumentParser(description="Create a version of Amiri with colored marks using COLR/CPAL tables.")
    parser.add_argument("arabicfile", metavar="FILE", help="input font to process")
    parser.add_argument("latinfile", metavar="FILE", help="input font to process")
    parser.add_argument("--out-file", metavar="FILE", help="output font to write", required=True)
    parser.add_argument("--feature-file", metavar="FILE", help="output font to write", required=True)
    parser.add_argument("--version", metavar="version", help="version number", required=True)

    args = parser.parse_args()

    font = merge(args)

    flags = ["round", "opentype", "no-mac-names"]
    font.generate(args.out_file, flags=flags)

if __name__ == "__main__":
    main()
