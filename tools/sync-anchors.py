import fontforge
import sys

font1 = fontforge.open(sys.argv[1])
font2 = fontforge.open(sys.argv[2])

anchor_names = sys.argv[3:]

for glyph1 in font1.glyphs():
    anchors1 = sorted(glyph1.anchorPoints)
    glyph2 = font2[glyph1.glyphname]
    anchors2 = sorted(glyph2.anchorPoints)
    anchors3 = []
    for i, anchor in enumerate(anchors1):
        if anchor[0] in anchor_names:
            anchors3.append(anchor)
        elif i >= len(anchors2):
            anchors3.append(anchor)
        else:
            anchors3.append(anchors2[i])
    if anchors3 != anchors2:
        glyph2.anchorPoints = anchors3

font2.save()
