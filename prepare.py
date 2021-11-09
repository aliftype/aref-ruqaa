import argparse

from datetime import datetime
from glyphsLib import GSFont


def build(args):
    font = GSFont(args.file)

    # Set metadata
    major, minor = args.version.split(".")
    font.versionMajor, font.versionMinor = int(major), int(minor)
    font.copyright = font.copyright.format(year=datetime.now().year)

    font.save(args.out_file)


def main():
    parser = argparse.ArgumentParser(description="Build Aref Ruqaa fonts.")
    parser.add_argument("file", metavar="FILE", help="input font to process")
    parser.add_argument(
        "--out-file", metavar="FILE", help="output font to write", required=True
    )
    parser.add_argument(
        "--version", metavar="version", help="version number", required=True
    )

    args = parser.parse_args()

    build(args)


if __name__ == "__main__":
    main()
