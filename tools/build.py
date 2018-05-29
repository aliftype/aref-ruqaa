#!/usr/bin/env python2
# encoding: utf-8

import argparse
import os
import string
import tempfile
import io
import operator

from datetime import datetime

from fontTools.ttLib import TTFont
from fontTools.feaLib import ast, parser, builder

import fontforge

from buildencoded import build as build_encoded

def merge(args):
    arabic = fontforge.open(args.arabicfile)
    arabic.encoding = "Unicode"

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
                    latin_locl = "feature locl {\nlookupflag IgnoreMarks; script latn;"
                latin_locl += "sub %s by %s;" % (name, glyph.glyphname)

    with tempfile.NamedTemporaryFile(mode="r") as tmp:
        latin.save(tmp.name)
        arabic.mergeFonts(tmp.name)

    with open(args.feature_file) as feature_file:
        features = string.Template(feature_file.read())
        with tempfile.NamedTemporaryFile(mode="w+") as tmp:
            arabic.generateFeatureFile(tmp.name)
            gpos = tmp.read()

    if latin_locl:
        latin_locl += "} locl;"
        features += "\n" + latin_locl

    features = features.substitute(GPOS=gpos)
    glyph_names = [n for n in arabic]

    # Parse the feature file and put all langsysstatement’s on the top
    fea = parser.Parser(io.StringIO(features), glyph_names).parse()
    langsys = {s.asFea(): s for s in fea.statements if isinstance(s, ast.LanguageSystemStatement)}
    statements = [s for s in fea.statements if not isinstance(s, ast.LanguageSystemStatement)]

    # Drop script and language statements from GPOS features (which are
    # generated from FontForge sources), so that they inherit from the
    # global languagesytem’s set in the feature file. This way I don’t have to manually repeat them.
    for statement in statements:
        if getattr(statement, "name", None) in ("curs", "mark", "mkmk"):
            scripts = []
            languages = []
            substatements = []
            for substatement in statement.statements:
                if isinstance(substatement, ast.ScriptStatement):
                    scripts.append(substatement.script)
                elif isinstance(substatement, ast.LanguageStatement):
                    languages.append(substatement.language)
                else:
                    substatements.append(substatement)
            if "latn" in scripts:
                # Not an Arabic feature, does nothing.
                continue
            # There must be one script and one language statement, otherwise
            # the lookups will be duplicated.
            assert len(scripts) == 1, statement
            assert len(languages) == 1, statement
            statement.statements = substatements

    # Make sure DFLT is the first.
    langsys = sorted(langsys.values(), key=operator.attrgetter("script"))
    fea.statements = langsys + statements

    for lookup in arabic.gsub_lookups + arabic.gpos_lookups:
        arabic.removeLookup(lookup)

    # Set metadata
    arabic.version = args.version
    copyright = 'Copyright © 2015-%s The Aref Ruqaa Project Authors, with Reserved Font Name "EURM10".' % datetime.now().year

    arabic.copyright = copyright.replace("©", "(c)")

    en = "English (US)"
    arabic.appendSFNTName(en, "Copyright", copyright)
    arabic.appendSFNTName(en, "Designer", "Abdullah Aref")
    arabic.appendSFNTName(en, "License URL", "http://scripts.sil.org/OFL")
    arabic.appendSFNTName(en, "License", 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL')
    arabic.appendSFNTName(en, "Descriptor", "Aref Ruqaa is an Arabic typeface that aspires to capture the essence of \
the classical Ruqaa calligraphic style.")
    arabic.appendSFNTName(en, "Sample Text", "الخط هندسة روحانية ظهرت بآلة جسمانية")
    arabic.appendSFNTName(en, "UniqueID", "%s;%s;%s" % (arabic.version, arabic.os2_vendor, arabic.fontname))

    return arabic, fea

def build(args):
    font, features = merge(args)

    build_encoded(font, features)

    with tempfile.NamedTemporaryFile(mode="r", suffix=args.out_file) as tmp:
        font.generate(tmp.name, flags=["round", "opentype"])
        ttfont = TTFont(tmp.name)

    try:
        builder.addOpenTypeFeatures(ttfont, features)
    except:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(features.asFea())
            print("Failed! Inspect temporary file: %r" % tmp.name)
        raise

    # Filter-out useless Macintosh names
    ttfont["name"].names = [n for n in ttfont["name"].names if n.platformID != 1]

    # https://github.com/fontforge/fontforge/pull/3235
    # fontDirectionHint is deprecated and must be set to 2
    ttfont["head"].fontDirectionHint = 2
    # unset bits 6..10
    ttfont["head"].flags &= ~0x7e0

    # Drop useless table with timestamp
    if "FFTM" in ttfont:
        del ttfont["FFTM"]

    ttfont.save(args.out_file)

def main():
    parser = argparse.ArgumentParser(description="Create a version of Amiri with colored marks using COLR/CPAL tables.")
    parser.add_argument("arabicfile", metavar="FILE", help="input font to process")
    parser.add_argument("latinfile", metavar="FILE", help="input font to process")
    parser.add_argument("--out-file", metavar="FILE", help="output font to write", required=True)
    parser.add_argument("--feature-file", metavar="FILE", help="output font to write", required=True)
    parser.add_argument("--version", metavar="version", help="version number", required=True)

    args = parser.parse_args()

    build(args)

if __name__ == "__main__":
    main()
