#!/usr/bin/env python2
# encoding: utf-8

import argparse
import os
import tempfile
import io
import operator

from datetime import datetime

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.feaLib import ast, parser, builder

import fontforge

from buildencoded import build as build_encoded

def parse_arabic_features(font, features):
    fea = parser.Parser(io.StringIO(features), font).parse()

    # Drop script and language statements from GPOS features (which are
    # generated from FontForge sources), so that they inherit from the global
    # languagesytem’s set in the feature file. This way I don’t have to
    # manually repeat them.
    langsys = {}
    statements = []
    for statement in fea.statements:
        name = getattr(statement, "name", "")
        if isinstance(statement, ast.LanguageSystemStatement):
            langsys[statement.asFea()] = statement
            continue
        if name in ("curs", "mark", "mkmk"):
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
            # There must be one script and one language statement, otherwise
            # the lookups will be duplicated.
            assert len(scripts) == 1, statement
            assert len(languages) == 1, statement
            statement.statements = substatements
        statements.append(statement)

    # Make sure DFLT is the first.
    langsys = sorted(langsys.values(), key=operator.attrgetter("script"))
    fea.statements = langsys + statements

    return fea


def parse_latin_features(font, features):
    # Parse the features and drop any languagesystem statement, they are
    # superfluous in FontForge generated features.
    fea = parser.Parser(io.StringIO(features), font).parse()

    fea.statements = [s for s in fea.statements
                      if not isinstance(s, ast.LanguageSystemStatement)]

    return fea


def merge_features(fea1, fea2):
    # Merge the GDEF classes, since that i the only thing duplicated.
    gdef = {}
    for statement in fea1.statements:
        name = getattr(statement, "name", "")
        if name.startswith("GDEF_"):
            gdef[name] = statement

    for statement in fea2.statements:
        name = getattr(statement, "name", "")
        if name.startswith("GDEF_"):
            if name in gdef:
                 gdef[name].glyphs.extend(statement.glyphSet())
                 continue
            gdef[name] = statement
        elif name == "GDEF":
            continue
        fea1.statements.append(statement)

    return fea1


def merge(args):
    arabic = fontforge.open(args.arabicfile)
    arabic.encoding = "Unicode"

    latin = fontforge.open(args.latinfile)
    latin.encoding = "Unicode"
    latin.em = arabic.em

    # If any Latin glyph exists in the Arabic font, rename it and add to a locl
    # feature.
    locl = []
    for glyph in latin.glyphs():
        if glyph.glyphname in arabic or glyph.unicode in arabic:
            name = arabic[glyph.unicode].glyphname
            glyph.unicode = -1
            glyph.glyphname += ".latn"
            locl.append("sub %s by %s;" % (name, glyph.glyphname))

    # Read external feature file.
    with open(args.feature_file) as feature_file:
        features = feature_file.read()

    # Add Arabic GPOS features from the SFD file.
    with tempfile.NamedTemporaryFile(mode="w+") as tmp:
        arabic.generateFeatureFile(tmp.name)
        features += tmp.read()
        arabic_fea = parse_arabic_features(arabic, features)

    # Add Latin features, must do before merging the fonts.
    with tempfile.NamedTemporaryFile(mode="w+") as tmp:
        latin.generateFeatureFile(tmp.name)
        features = tmp.read()
        if locl:
            features += "feature locl {\nlookupflag IgnoreMarks; script latn;"
            features += "\n".join(locl)
            features += "} locl;"
        latin_fea = parse_latin_features(latin, features)

    # Merge Arabic and Latin fonts
    with tempfile.NamedTemporaryFile(mode="r") as tmp:
        latin.save(tmp.name)
        arabic.mergeFonts(tmp.name)

    fea = merge_features(arabic_fea, latin_fea)

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

    # Drop useless table with timestamp
    if "FFTM" in ttfont:
        del ttfont["FFTM"]

    unicodes = [g.unicode for g in font.glyphs() if g.unicode > 0]

    options = subset.Options()
    options.set(layout_features='*', name_IDs='*', name_languages='*',
        notdef_outline=True, glyph_names=True)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(ttfont)

    # Filter-out useless Macintosh names
    ttfont["name"].names = [n for n in ttfont["name"].names if n.platformID != 1]

    # https://github.com/fontforge/fontforge/pull/3235
    # fontDirectionHint is deprecated and must be set to 2
    ttfont["head"].fontDirectionHint = 2
    # unset bits 6..10
    ttfont["head"].flags &= ~0x7e0

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
