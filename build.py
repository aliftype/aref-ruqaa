import argparse
import io

from datetime import datetime

from ufo2ft import compileTTF

from glyphsLib import GSFont
from glyphsLib.builder.builders import UFOBuilder


def build(args):
    font = GSFont(args.file)

    # Set metadata
    major, minor = args.version.split(".")
    font.versionMajor, font.versionMinor = int(major), int(minor)
    font.copyright = font.copyright.format(year=datetime.now().year)

    builder = UFOBuilder(
        font,
        propagate_anchors=False,
        write_skipexportglyphs=True,
        store_editor_state=False,
    )
    for master in builder.masters:
        if master.info.styleName == args.master:
            ufo = master
            break

    compileTTF(
        ufo, inplace=True, flattenComponents=True, useProductionNames=False
    ).save(args.out_file)


def main():
    parser = argparse.ArgumentParser(description="Build Aref Ruqaa fonts.")
    parser.add_argument("file", metavar="FILE", help="input font to process")
    parser.add_argument(
        "--out-file", metavar="FILE", help="output font to write", required=True
    )
    parser.add_argument(
        "--master", metavar="NAME", help="name of the master to build", required=True
    )
    parser.add_argument(
        "--version", metavar="version", help="version number", required=True
    )

    args = parser.parse_args()

    build(args)


if __name__ == "__main__":
    main()
