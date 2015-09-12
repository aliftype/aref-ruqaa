from sortsmill import ffcompat as fontforge
import sys

font = fontforge.open(sys.argv[1])

bad_glyph_classes = {}
for glyph in font.glyphs():
    if glyph.glyphclass not in ("mark", "baseglyph"):
        if glyph.glyphclass in bad_glyph_classes:
            bad_glyph_classes[glyph.glyphclass].append(glyph.glyphname)
        else:
            bad_glyph_classes[glyph.glyphclass] = [glyph.glyphname]

if bad_glyph_classes:
    from pprint import pformat
    print >> sys.stderr, "Some glyphs have bad glyph class:"
    print >> sys.stderr, pformat(bad_glyph_classes)
    sys.exit(1)

with open(sys.argv[2], "w") as log:
    print >> log, "All tests passed"
sys.exit(0)
