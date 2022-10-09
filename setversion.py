import argparse
from glyphsLib import GSFont


def main():
    parser = argparse.ArgumentParser(description="Build Aref Ruqaa fonts.")
    parser.add_argument("file", metavar="FILE", help="input font to process")
    parser.add_argument("outfile", metavar="FILE", help="output font to write")
    parser.add_argument("version", metavar="version", help="version number")

    args = parser.parse_args()

    font = GSFont(args.file)
    font.versionMajor, font.versionMinor = [int(x) for x in args.version.split(".")]
    font.save(args.outfile)


if __name__ == "__main__":
    main()
