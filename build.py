import argparse
import io

from datetime import datetime

from sfdLib.parser import SFDParser

from ufo2ft import compileTTF

from ufoLib2 import Font

from fontTools.misc.fixedTools import otRound


def _dumpAnchor(anchor):
    if not anchor:
        return "<anchor NULL>"
    return f"<anchor {otRound(anchor.x)} {otRound(anchor.y)}>"


def build(args):
    font = Font(validate=False)
    SFDParser(
        args.file,
        font,
        ufo_anchors=True,
        ufo_kerning=True,
        minimal=False,
    ).parse()

    lookups = {}
    lines = []

    for glyph in font:
        for anchor in glyph.anchors:
            if anchor.name in ("entry", "exit"):
                lookups.setdefault("curs", {}).setdefault(glyph.name, [None, None])
                lookups["curs"][glyph.name][0 if anchor.name == "entry" else 1] = anchor
            else:
                name = anchor.name
                if name.startswith("_"):
                    name = name[1:]
                lookup = name.split(".")[0].title()
                if name.endswith(".mkmk"):
                    lookup = f"mkmk{lookup}"
                else:
                    lookup = f"mark{lookup}"
                lookups.setdefault(lookup, {}).setdefault(glyph.name, []).append(anchor)

    for lookup in sorted(lookups):
        lines.append(f"lookup {lookup} {{")
        if lookup == "curs":
            lines.append("lookupflag RightToLeft IgnoreMarks;")
            for glyph, (entry, exit_) in lookups[lookup].items():
                lines.append(f"pos cursive {glyph} {_dumpAnchor(entry)} {_dumpAnchor(exit_)};")
        else:
            type_ = "base"
            if lookup.startswith("mkmk"):
                type_ = "mark"
                glyphs = " ".join([g for g in lookups[lookup].keys()])
                lines.append(f"lookupflag UseMarkFilteringSet [{glyphs}];")
            for glyph, anchors in lookups[lookup].items():
                for anchor in anchors:
                    if not anchor.name.startswith("_"):
                        continue
                    lines.append(f"markClass {glyph} {_dumpAnchor(anchor)} @{anchor.name[1:]};")
            for glyph, anchors in lookups[lookup].items():
                if all([a.name.startswith("_") for a in anchors]):
                    continue
                line = f"pos {type_} {glyph} "
                for anchor in anchors:
                    if anchor.name.startswith("_"):
                        continue
                    line += f"{_dumpAnchor(anchor)} mark @{anchor.name} "
                line += ";"
                lines.append(line)
        lines.append(f"}} {lookup};")

    font.features.text = "\n".join(lines)

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
