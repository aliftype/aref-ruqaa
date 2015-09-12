from sortsmill import ffcompat as fontforge
import sys

font = fontforge.open(sys.argv[1])

bad_glyph_classes = {}
bad_side_bearings = {}

for glyph in font.glyphs():
    if glyph.glyphclass not in ("mark", "baseglyph"):
        if glyph.glyphclass not in bad_glyph_classes:
            bad_glyph_classes[glyph.glyphclass] = []
        bad_glyph_classes[glyph.glyphclass].append(glyph.glyphname)
    if ".init" in glyph.glyphname or ".isol" in glyph.glyphname:
        if "arKaf.init" not in glyph.glyphname:
            if glyph.right_side_bearing <= 0:
                if "left" not in bad_side_bearings:
                    bad_side_bearings["left"] = []
                bad_side_bearings["left"].append(glyph.glyphname)

if bad_glyph_classes:
    from pprint import pformat
    print >> sys.stderr, "Some glyphs have bad glyph class:"
    print >> sys.stderr, pformat(bad_glyph_classes)
    sys.exit(1)

if bad_side_bearings:
    from pprint import pformat
    print >> sys.stderr, "Some glyphs have bad side bearings:"
    print >> sys.stderr, pformat(bad_side_bearings)
    sys.exit(1)

with open(sys.argv[2], "w") as log:
    print >> log, "All tests passed"
sys.exit(0)
