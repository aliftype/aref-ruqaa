import argparse
import io

from datetime import datetime

from fontTools.ttLib import TTFont
from fontTools.feaLib import ast, parser, builder

from sfdLib.parser import SFDParser

from ufo2ft import compileTTF

from ufoLib2 import Font


def parse_features(font):
    fea = parser.Parser(io.StringIO(font.features.text), font.glyphOrder).parse()

    # Drop script and language statements from GPOS features (which are
    # generated from sources), so that they inherit from the global
    # languagesytem’s set in the feature file. This way I don’t have to
    # manually repeat them.
    langsys = []
    statements = []
    for statement in fea.statements:
        name = getattr(statement, "name", "")
        if isinstance(statement, ast.LanguageSystemStatement):
            langsys.append(statement)
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

    fea.statements = langsys + statements

    return fea


def build(args):
    font = Font(validate=False)
    SFDParser(
        args.file,
        font,
        ignore_uvs=False,
        ufo_anchors=False,
        ufo_kerning=False,
        minimal=True,
    ).parse()

    # Read external feature file.
    with open(args.feature_file) as feature_file:
        font.features.text = feature_file.read() + font.features.text

    # Add Arabic GPOS features from the SFD file.
    fea = parse_features(font)

    # Set metadata
    info = font.info

    major, minor = args.version.split(".")
    info.versionMajor, info.versionMinor = int(major), int(minor)
    year = datetime.now().year
    info.copyright = f"Copyright 2015-{year} The Aref Ruqaa Project Authors (https://github.com/alif-type/aref-ruqaa), with Reserved Font Name EURM10."
    info.openTypeNameDesigner = "Abdullah Aref"
    info.openTypeNameLicenseURL = "https://scripts.sil.org/OFL"
    info.openTypeNameLicense = "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://scripts.sil.org/OFL"
    info.openTypeNameDescription = "Aref Ruqaa is an Arabic typeface that aspires to capture the essence of \
the classical Ruqaa calligraphic style."
    info.openTypeNameSampleText = "الخط هندسة روحانية ظهرت بآلة جسمانية"

    font.features.text = str(fea)

    compileTTF(font, inplace=True).save(args.out_file)


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
