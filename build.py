import argparse
import io

from datetime import datetime

from sfdLib.parser import SFDParser

from ufo2ft import compileTTF

from ufoLib2 import Font


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
        font.features.text += feature_file.read()

    # Set metadata
    info = font.info

    major, minor = args.version.split(".")
    info.versionMajor, info.versionMinor = int(major), int(minor)
    info.copyright = info.copyright.format(year=datetime.now().year)

    compileTTF(font, inplace=True, flattenComponents=True).save(args.out_file)


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
