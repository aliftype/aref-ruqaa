import argparse
import os
import tempfile
import io
import operator

from datetime import datetime

from fontTools.ttLib import TTFont
from fontTools.feaLib import ast, parser, builder

import fontforge


def parse_features(font, features):
    glyphs = set(g.glyphname for g in font.glyphs())
    fea = parser.Parser(io.StringIO(features), glyphs).parse()

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


def prepare(args):
    font = fontforge.open(args.file)
    font.encoding = "Unicode"

    # Read external feature file.
    with open(args.feature_file) as feature_file:
        features = feature_file.read()

    # Add font GPOS features from the SFD file.
    with tempfile.NamedTemporaryFile(mode="w+") as tmp:
        font.generateFeatureFile(tmp.name)
        features += tmp.read()
        fea = parse_features(font, features)

    # Set metadata
    font.version = args.version
    year = datetime.now().year
    font.copyright = (
        "Copyright 2015-%s The Aref Ruqaa Project Authors (https://github.com/alif-type/aref-ruqaa), with Reserved Font Name EURM10."
        % datetime.now().year
    )

    en = "English (US)"
    font.appendSFNTName(en, "Version", "Version %s" % font.version)
    font.appendSFNTName(en, "Designer", "Abdullah Aref")
    font.appendSFNTName(en, "License URL", "https://scripts.sil.org/OFL")
    font.appendSFNTName(
        en,
        "License",
        "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://scripts.sil.org/OFL",
    )
    font.appendSFNTName(
        en,
        "Descriptor",
        "Aref Ruqaa is an font typeface that aspires to capture the essence of \
the classical Ruqaa calligraphic style.",
    )
    font.appendSFNTName(en, "Sample Text", "الخط هندسة روحانية ظهرت بآلة جسمانية")
    font.appendSFNTName(
        en,
        "UniqueID",
        "%s;%s;%s" % (font.version, font.os2_vendor, font.fontname),
    )

    return font, fea


def build(args):
    font, features = prepare(args)

    with tempfile.NamedTemporaryFile(mode="r", suffix=os.path.basename(args.out_file)) as tmp:
        font.generate(tmp.name, flags=["round", "opentype", "dummy-dsig", "no-hints"])
        ttfont = TTFont(tmp.name)

    try:
        builder.addOpenTypeFeatures(ttfont, features)
    except:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(features.asFea())
            print("Failed! Inspect temporary file: %r" % tmp.name)
        raise

    ttfont.save(args.out_file)


def main():
    parser = argparse.ArgumentParser(description="Build Aref Ruqaa fonts.")
    parser.add_argument("file", metavar="FILE", help="input font to process")
    parser.add_argument(
        "--out-file", metavar="FILE", help="output font to write", required=True
    )
    parser.add_argument(
        "--feature-file", metavar="FILE", help="input feature file", required=True
    )
    parser.add_argument(
        "--version", metavar="version", help="version number", required=True
    )

    args = parser.parse_args()

    build(args)


if __name__ == "__main__":
    main()
