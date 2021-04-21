import argparse
import io

from datetime import datetime

from ufo2ft import compileTTF

from glyphsLib import GSFont
from glyphsLib.builder.builders import UFOBuilder

from fontTools.misc.fixedTools import otRound


def _dumpAnchor(anchor):
    if not anchor:
        return "<anchor NULL>"
    return f"<anchor {otRound(anchor.x)} {otRound(anchor.y)}>"


def build(args):
    glyphs = GSFont(args.file)

    builder = UFOBuilder(
        glyphs,
        propagate_anchors=False,
        write_skipexportglyphs=True,
        store_editor_state=False,
    )
    for master in builder.masters:
        if master.info.styleName == args.master:
            font = master

    anchors = {}
    curs = []
    curs.append("lookupflag RightToLeft IgnoreMarks;")
    for glyph in font:
        for anchor in glyph.anchors:
            if anchor.name in ("entry", "exit"):
                anchors.setdefault(glyph.name, [None, None])
                anchors[glyph.name][0 if anchor.name == "entry" else 1] = anchor
    for glyph, (entry, exit_) in anchors.items():
        curs.append(f"pos cursive {glyph} {_dumpAnchor(entry)} {_dumpAnchor(exit_)};")

    curs = "\n".join(curs) + "\n"
    font.features.text = font.features.text.replace("# Automatic Code Cursive", curs)

    # Set metadata
    info = font.info

    major, minor = args.version.split(".")
    info.versionMajor, info.versionMinor = int(major), int(minor)
    info.copyright = info.copyright.format(year=datetime.now().year)

    compileTTF(
        font, inplace=True, flattenComponents=True, useProductionNames=False
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
