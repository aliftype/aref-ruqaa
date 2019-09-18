import fontforge
import sys

font1 = fontforge.open(sys.argv[1])
font2 = fontforge.open(sys.argv[2])

for glyph1 in font1.glyphs():
    glyph2 = font2[glyph1.glyphname]

    anchors1 = sorted(glyph1.anchorPoints)
    anchors2 = sorted(glyph2.anchorPoints)
    anchors3 = []

    anchors2_names = [a[0] for a in anchors2]
    for i, anchor in enumerate(anchors1):
        if anchor[0] not in anchors2_names:
            anchors3.append(anchor)
    anchors3 = set(anchors2 + anchors3)
    if anchors3 != set(anchors2):
        glyph2.anchorPoints = tuple(anchors3)

font2.save(sys.argv[2])
