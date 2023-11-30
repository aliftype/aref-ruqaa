import argparse
import shutil
import openstep_plist


def main():
    parser = argparse.ArgumentParser(description="Build Aref Ruqaa fonts.")
    parser.add_argument("file", metavar="FILE", help="input font to process")
    parser.add_argument("outfile", metavar="FILE", help="output font to write")
    parser.add_argument("version", metavar="version", help="version number")

    args = parser.parse_args()

    shutil.copytree(args.file, args.outfile, dirs_exist_ok=True)

    fontinfo = f"{args.outfile}/fontinfo.plist"
    with open(fontinfo, "r") as f:
        info = openstep_plist.load(f, use_numbers=True)

    major, minor = args.version.split(".")
    info["versionMajor"] = int(major)
    info["versionMinor"] = int(minor)

    with open(fontinfo, "wb") as f:
        openstep_plist.dump(info, f)


if __name__ == "__main__":
    main()
