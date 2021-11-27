import argparse
import copy
import logging

from fontTools import merge, subset
from fontTools import configLogger
from fontTools.ttLib import TTFont


def main():
    parser = argparse.ArgumentParser(description="Merge Aref Ruqaa fonts.")
    parser.add_argument("file1", metavar="FILE", help="input font to process")
    parser.add_argument("file2", metavar="FILE", help="input font to process")
    parser.add_argument("--color", action="store_true", help="merge color tables")
    parser.add_argument("--family", metavar="STR", help="base family name")
    parser.add_argument("--suffix", metavar="STR", help="suffix to add to family name")
    parser.add_argument(
        "--out-file", metavar="FILE", help="output font to write", required=True
    )

    args = parser.parse_args()

    configLogger(level=logging.ERROR)

    merger = merge.Merger()
    font = merger.merge([args.file1, args.file2])

    if args.color:
        orig = TTFont(args.file1)
        font["CPAL"] = copy.deepcopy(orig["CPAL"])
        font["COLR"] = copy.deepcopy(orig["COLR"])

        name = font["name"]
        family = args.family
        psname = args.family.replace(" ", "")
        for rec in name.names:
            if rec.nameID in (1, 3, 4, 6):
                rec.string = (
                    str(rec)
                    .replace(family, family + " " + args.suffix)
                    .replace(psname, psname + args.suffix)
                )

    # Drop incomplete Greek support.
    unicodes = set(font.getBestCmap().keys()) - set(range(0x0370, 0x03FF))

    options = subset.Options()
    options.set(
        layout_features="*",
        layout_scripts=["arab", "latn", "DFLT"],
        name_IDs="*",
        name_languages="*",
        notdef_outline=True,
        glyph_names=False,
        recalc_average_width=True,
    )
    if not args.color:
        options.set(drop_tables=["CPAL", "COLR"])
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(font)

    font.save(args.out_file)


if __name__ == "__main__":
    main()
